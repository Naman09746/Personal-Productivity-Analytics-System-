"""
Analytics router - Performance metrics and reports
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from typing import Optional

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.analytics import TodayStats, WeeklyAnalytics, MonthlyAnalytics, TrendData
from services.score_engine import ScoreEngine
from services.explainer import Explainer
from services.aggregator import Aggregator

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/today", response_model=TodayStats)
async def get_today_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quick stats for today"""
    today = date.today()
    
    daily_score = await ScoreEngine.calculate_daily_score(db, current_user.id, today)
    streak = await ScoreEngine.calculate_streak(db, current_user.id)
    
    # Check physical activity
    from services.rule_engine import RuleEngine
    physical_entry = await RuleEngine.get_physical_entry_for_date(db, current_user.id, today)
    
    return TodayStats(
        date=today,
        completed=daily_score["completed"],
        total=daily_score["total"],
        completion_rate=daily_score["completion_rate"],
        streak_days=streak,
        physical_done=physical_entry is not None
    )


@router.get("/week", response_model=WeeklyAnalytics)
async def get_current_week_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for current week"""
    week_start, _ = ScoreEngine.get_week_bounds(date.today())
    return await _get_week_analytics(db, current_user.id, week_start)


@router.get("/week/{week_start}", response_model=WeeklyAnalytics)
async def get_week_analytics(
    week_start: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a specific week"""
    return await _get_week_analytics(db, current_user.id, week_start)


@router.get("/month", response_model=MonthlyAnalytics)
async def get_current_month_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for current month"""
    today = date.today()
    return await _get_month_analytics(db, current_user.id, today.year, today.month)


@router.get("/month/{year}/{month}", response_model=MonthlyAnalytics)
async def get_month_analytics(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a specific month"""
    return await _get_month_analytics(db, current_user.id, year, month)


@router.get("/trends", response_model=TrendData)
async def get_trends(
    period: str = "weekly",
    lookback: int = 8,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend data for charts"""
    labels = []
    completion_rates = []
    weighted_scores = []
    consistency_scores = []
    
    today = date.today()
    
    if period == "weekly":
        current_week, _ = ScoreEngine.get_week_bounds(today)
        
        for i in range(lookback - 1, -1, -1):
            week_start = current_week - timedelta(weeks=i)
            score = await ScoreEngine.calculate_weekly_score(db, current_user.id, week_start)
            
            labels.append(week_start.strftime("%b %d"))
            completion_rates.append(score["completion_rate"])
            weighted_scores.append(score["weighted_score"])
            consistency_scores.append(score["consistency_score"])
    else:
        # Monthly
        current_month = today.month
        current_year = today.year
        
        for i in range(lookback - 1, -1, -1):
            month = current_month - i
            year = current_year
            while month <= 0:
                month += 12
                year -= 1
            
            report = await Aggregator.generate_monthly_report(db, current_user.id, year, month)
            
            labels.append(date(year, month, 1).strftime("%b %Y"))
            completion_rates.append(report.avg_completion_rate)
            weighted_scores.append(report.avg_weighted_score)
            consistency_scores.append(50 + report.consistency_trend)  # Normalize
    
    return TrendData(
        period=period,
        labels=labels,
        completion_rates=completion_rates,
        weighted_scores=weighted_scores,
        consistency_scores=consistency_scores
    )


async def _get_week_analytics(
    db: AsyncSession,
    user_id,
    week_start: date
) -> WeeklyAnalytics:
    """Build weekly analytics response"""
    score = await ScoreEngine.calculate_weekly_score(db, user_id, week_start)
    insights = await Explainer.explain_weekly_change(db, user_id, week_start)
    
    # Get last week for comparison
    last_week_start = week_start - timedelta(days=7)
    last_week_score = await ScoreEngine.calculate_weekly_score(db, user_id, last_week_start)
    comparison = None
    if last_week_score["total_possible"] > 0:
        comparison = score["completion_rate"] - last_week_score["completion_rate"]
    
    return WeeklyAnalytics(
        week_start=week_start,
        week_end=week_start + timedelta(days=6),
        completion_rate=score["completion_rate"],
        weighted_score=score["weighted_score"],
        consistency_score=score["consistency_score"],
        total_completed=score["total_completed"],
        total_possible=score["total_possible"],
        habit_breakdown=score["habit_breakdown"],
        insights=insights,
        daily_rates=score["daily_rates"],
        comparison_to_last_week=round(comparison, 1) if comparison else None
    )


async def _get_month_analytics(
    db: AsyncSession,
    user_id,
    year: int,
    month: int
) -> MonthlyAnalytics:
    """Build monthly analytics response"""
    report = await Aggregator.generate_monthly_report(db, user_id, year, month)
    
    # Get weekly scores for the month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    weekly_scores = []
    current = first_day - timedelta(days=first_day.weekday())
    while current <= last_day:
        score = await ScoreEngine.calculate_weekly_score(db, user_id, current)
        weekly_scores.append(score["weighted_score"])
        current += timedelta(days=7)
    
    return MonthlyAnalytics(
        month=month,
        year=year,
        avg_completion_rate=report.avg_completion_rate,
        avg_weighted_score=report.avg_weighted_score,
        consistency_trend=report.consistency_trend,
        performance_grade=report.performance_grade,
        top_habits=report.top_habits,
        struggling_habits=report.struggling_habits,
        weekly_scores=weekly_scores,
        score_explanation=report.score_explanation
    )
