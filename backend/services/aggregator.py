"""
Aggregator - Weekly and monthly data aggregation
"""
from datetime import date, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.score import WeeklyScore, MonthlyScore
from services.score_engine import ScoreEngine
from services.explainer import Explainer


class Aggregator:
    """Handles weekly and monthly data aggregation"""
    
    @staticmethod
    async def generate_weekly_report(
        db: AsyncSession,
        user_id: UUID,
        week_start: date
    ) -> WeeklyScore:
        """Generate and store weekly report"""
        # Calculate scores
        score_data = await ScoreEngine.calculate_weekly_score(db, user_id, week_start)
        insights = await Explainer.explain_weekly_change(db, user_id, week_start)
        
        # Check if report already exists
        existing = await db.execute(
            select(WeeklyScore).where(
                and_(
                    WeeklyScore.user_id == user_id,
                    WeeklyScore.week_start == week_start
                )
            )
        )
        weekly_score = existing.scalar_one_or_none()
        
        if weekly_score:
            # Update existing
            weekly_score.completion_rate = score_data["completion_rate"]
            weekly_score.weighted_score = score_data["weighted_score"]
            weekly_score.consistency_score = score_data["consistency_score"]
            weekly_score.total_completed = score_data["total_completed"]
            weekly_score.total_possible = score_data["total_possible"]
            weekly_score.habit_breakdown = score_data["habit_breakdown"]
            weekly_score.insights = insights
        else:
            # Create new
            weekly_score = WeeklyScore(
                user_id=user_id,
                week_start=week_start,
                completion_rate=score_data["completion_rate"],
                weighted_score=score_data["weighted_score"],
                consistency_score=score_data["consistency_score"],
                total_completed=score_data["total_completed"],
                total_possible=score_data["total_possible"],
                habit_breakdown=score_data["habit_breakdown"],
                insights=insights
            )
            db.add(weekly_score)
        
        await db.flush()
        return weekly_score
    
    @staticmethod
    async def generate_monthly_report(
        db: AsyncSession,
        user_id: UUID,
        year: int,
        month: int
    ) -> MonthlyScore:
        """Generate and store monthly report"""
        # Get all weekly scores for the month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        result = await db.execute(
            select(WeeklyScore).where(
                and_(
                    WeeklyScore.user_id == user_id,
                    WeeklyScore.week_start >= first_day,
                    WeeklyScore.week_start <= last_day
                )
            ).order_by(WeeklyScore.week_start)
        )
        weekly_scores = result.scalars().all()
        
        if not weekly_scores:
            # Generate weekly reports first
            current = first_day - timedelta(days=first_day.weekday())  # Monday
            while current <= last_day:
                await Aggregator.generate_weekly_report(db, user_id, current)
                current += timedelta(days=7)
            
            # Fetch again
            result = await db.execute(
                select(WeeklyScore).where(
                    and_(
                        WeeklyScore.user_id == user_id,
                        WeeklyScore.week_start >= first_day,
                        WeeklyScore.week_start <= last_day
                    )
                ).order_by(WeeklyScore.week_start)
            )
            weekly_scores = result.scalars().all()
        
        # Calculate monthly aggregates
        if weekly_scores:
            avg_completion = sum(w.completion_rate for w in weekly_scores) / len(weekly_scores)
            avg_weighted = sum(w.weighted_score for w in weekly_scores) / len(weekly_scores)
            
            # Consistency trend
            if len(weekly_scores) > 1:
                first_half = weekly_scores[:len(weekly_scores)//2]
                second_half = weekly_scores[len(weekly_scores)//2:]
                first_avg = sum(w.consistency_score for w in first_half) / len(first_half)
                second_avg = sum(w.consistency_score for w in second_half) / len(second_half)
                consistency_trend = second_avg - first_avg
            else:
                consistency_trend = 0
            
            weekly_rates = [w.completion_rate for w in weekly_scores]
        else:
            avg_completion = 0
            avg_weighted = 0
            consistency_trend = 0
            weekly_rates = []
        
        grade = Explainer.generate_grade(avg_weighted)
        
        # Aggregate habit performance across weeks
        habit_totals = {}
        for week in weekly_scores:
            for habit in week.habit_breakdown:
                hid = habit["habit_id"]
                if hid not in habit_totals:
                    habit_totals[hid] = {
                        "habit_id": hid,
                        "habit_name": habit["habit_name"],
                        "category": habit["category"],
                        "total_rate": 0,
                        "count": 0,
                        "weight": habit["weight"]
                    }
                habit_totals[hid]["total_rate"] += habit["completion_rate"]
                habit_totals[hid]["count"] += 1
        
        # Calculate averages and sort
        habit_avgs = []
        for h in habit_totals.values():
            avg = h["total_rate"] / h["count"] if h["count"] > 0 else 0
            habit_avgs.append({
                "habit_id": h["habit_id"],
                "habit_name": h["habit_name"],
                "category": h["category"],
                "completion_rate": round(avg, 1),
                "weight": h["weight"]
            })
        
        habit_avgs.sort(key=lambda x: x["completion_rate"], reverse=True)
        top_habits = habit_avgs[:3]
        struggling_habits = [h for h in habit_avgs if h["completion_rate"] < 70][-3:]
        
        # Generate explanation
        explanations = []
        if avg_completion >= 80:
            explanations.append({
                "icon": "🏆",
                "message": f"Excellent month! Average completion was {avg_completion:.1f}%",
                "impact": avg_completion / 10
            })
        elif avg_completion >= 60:
            explanations.append({
                "icon": "💪",
                "message": f"Good progress. Average completion was {avg_completion:.1f}%",
                "impact": avg_completion / 10
            })
        else:
            explanations.append({
                "icon": "🎯",
                "message": f"Room for improvement. Average completion was {avg_completion:.1f}%",
                "impact": avg_completion / 10
            })
        
        if consistency_trend > 5:
            explanations.append({
                "icon": "📈",
                "message": "Consistency improved throughout the month",
                "impact": consistency_trend / 10
            })
        elif consistency_trend < -5:
            explanations.append({
                "icon": "📉",
                "message": "Consistency declined towards end of month",
                "impact": consistency_trend / 10
            })
        
        # Check if exists
        existing = await db.execute(
            select(MonthlyScore).where(
                and_(
                    MonthlyScore.user_id == user_id,
                    MonthlyScore.year == year,
                    MonthlyScore.month == month
                )
            )
        )
        monthly_score = existing.scalar_one_or_none()
        
        if monthly_score:
            monthly_score.avg_completion_rate = avg_completion
            monthly_score.avg_weighted_score = avg_weighted
            monthly_score.consistency_trend = consistency_trend
            monthly_score.performance_grade = grade
            monthly_score.top_habits = top_habits
            monthly_score.struggling_habits = struggling_habits
            monthly_score.score_explanation = explanations
        else:
            monthly_score = MonthlyScore(
                user_id=user_id,
                month=month,
                year=year,
                avg_completion_rate=avg_completion,
                avg_weighted_score=avg_weighted,
                consistency_trend=consistency_trend,
                performance_grade=grade,
                top_habits=top_habits,
                struggling_habits=struggling_habits,
                score_explanation=explanations
            )
            db.add(monthly_score)
        
        await db.flush()
        return monthly_score
