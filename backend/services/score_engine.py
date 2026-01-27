"""
Score Engine - Calculate habit scores and metrics
"""
from datetime import date, timedelta
from uuid import UUID
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import statistics

from models.habit import Habit
from models.entry import DailyEntry


class ScoreEngine:
    """Calculates habit scores and performance metrics"""
    
    @staticmethod
    def get_week_bounds(target_date: date) -> tuple[date, date]:
        """Get Monday (start) and Sunday (end) of the week containing target_date"""
        days_since_monday = target_date.weekday()
        week_start = target_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    
    @staticmethod
    async def calculate_daily_score(
        db: AsyncSession,
        user_id: UUID,
        target_date: date
    ) -> Dict:
        """Calculate score for a single day"""
        # Get active habits
        habits_result = await db.execute(
            select(Habit).where(
                and_(Habit.user_id == user_id, Habit.is_active == True)
            )
        )
        habits = habits_result.scalars().all()
        
        if not habits:
            return {
                "date": target_date,
                "completion_rate": 0.0,
                "weighted_score": 0.0,
                "completed": 0,
                "total": 0
            }
        
        # Get entries for the date
        entries_result = await db.execute(
            select(DailyEntry).where(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.entry_date == target_date,
                    DailyEntry.completed == True
                )
            )
        )
        entries = entries_result.scalars().all()
        
        completed_habit_ids = {e.habit_id for e in entries}
        
        # Calculate scores
        total_habits = len(habits)
        completed_count = sum(1 for h in habits if h.id in completed_habit_ids)
        
        total_weight = sum(h.weight for h in habits)
        weighted_completed = sum(
            h.weight for h in habits if h.id in completed_habit_ids
        )
        
        completion_rate = (completed_count / total_habits * 100) if total_habits > 0 else 0
        weighted_score = (weighted_completed / total_weight * 100) if total_weight > 0 else 0
        
        return {
            "date": target_date,
            "completion_rate": round(completion_rate, 1),
            "weighted_score": round(weighted_score, 1),
            "completed": completed_count,
            "total": total_habits
        }
    
    @staticmethod
    async def calculate_weekly_score(
        db: AsyncSession,
        user_id: UUID,
        week_start: date
    ) -> Dict:
        """Calculate comprehensive weekly score with habit breakdown"""
        week_end = week_start + timedelta(days=6)
        
        # Get active habits
        habits_result = await db.execute(
            select(Habit).where(
                and_(Habit.user_id == user_id, Habit.is_active == True)
            )
        )
        habits = habits_result.scalars().all()
        
        if not habits:
            return ScoreEngine._empty_weekly_score(week_start, week_end)
        
        # Get all entries for the week
        entries_result = await db.execute(
            select(DailyEntry).where(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.entry_date >= week_start,
                    DailyEntry.entry_date <= week_end,
                    DailyEntry.completed == True
                )
            )
        )
        entries = entries_result.scalars().all()
        
        # Build entries lookup
        entries_by_habit = {}
        for entry in entries:
            if entry.habit_id not in entries_by_habit:
                entries_by_habit[entry.habit_id] = []
            entries_by_habit[entry.habit_id].append(entry.entry_date)
        
        # Calculate per-habit breakdown
        habit_breakdown = []
        total_weight = sum(h.weight for h in habits)
        
        for habit in habits:
            completed_count = len(entries_by_habit.get(habit.id, []))
            target = habit.target_per_week
            rate = min(completed_count / target * 100, 100) if target > 0 else 0
            weighted_contribution = (habit.weight / total_weight * rate) if total_weight > 0 else 0
            
            habit_breakdown.append({
                "habit_id": str(habit.id),
                "habit_name": habit.name,
                "category": habit.category,
                "completed_count": completed_count,
                "target_count": target,
                "completion_rate": round(rate, 1),
                "weight": habit.weight,
                "weighted_contribution": round(weighted_contribution, 1),
                "is_below_threshold": rate < habit.goal_threshold
            })
        
        # Calculate daily rates for consistency
        daily_rates = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_entries = [e for e in entries if e.entry_date == day]
            day_rate = len(day_entries) / len(habits) * 100 if habits else 0
            daily_rates.append(round(day_rate, 1))
        
        # Calculate consistency (inverse of variance)
        if len(daily_rates) > 1:
            variance = statistics.variance(daily_rates)
            consistency = max(0, 100 - (variance / 10))
        else:
            consistency = 100
        
        # Overall scores
        total_completed = len(entries)
        total_possible = sum(h.target_per_week for h in habits)
        completion_rate = (total_completed / total_possible * 100) if total_possible > 0 else 0
        weighted_score = sum(hb["weighted_contribution"] for hb in habit_breakdown)
        
        return {
            "week_start": week_start,
            "week_end": week_end,
            "completion_rate": round(completion_rate, 1),
            "weighted_score": round(weighted_score, 1),
            "consistency_score": round(consistency, 1),
            "total_completed": total_completed,
            "total_possible": total_possible,
            "habit_breakdown": habit_breakdown,
            "daily_rates": daily_rates
        }
    
    @staticmethod
    def _empty_weekly_score(week_start: date, week_end: date) -> Dict:
        return {
            "week_start": week_start,
            "week_end": week_end,
            "completion_rate": 0.0,
            "weighted_score": 0.0,
            "consistency_score": 0.0,
            "total_completed": 0,
            "total_possible": 0,
            "habit_breakdown": [],
            "daily_rates": [0.0] * 7
        }
    
    @staticmethod
    async def calculate_streak(
        db: AsyncSession,
        user_id: UUID
    ) -> int:
        """Calculate current streak of consecutive days with at least one habit completed"""
        today = date.today()
        streak = 0
        check_date = today
        
        while True:
            result = await db.execute(
                select(func.count(DailyEntry.id)).where(
                    and_(
                        DailyEntry.user_id == user_id,
                        DailyEntry.entry_date == check_date,
                        DailyEntry.completed == True
                    )
                )
            )
            count = result.scalar()
            
            if count > 0:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
            
            # Safety limit
            if streak > 365:
                break
        
        return streak
