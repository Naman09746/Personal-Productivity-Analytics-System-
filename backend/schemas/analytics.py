"""
Analytics schemas
"""
from pydantic import BaseModel
from datetime import date
from typing import Optional


class TodayStats(BaseModel):
    """Quick stats for today"""
    date: date
    completed: int
    total: int
    completion_rate: float
    streak_days: int
    physical_done: bool


class HabitBreakdown(BaseModel):
    """Per-habit analytics"""
    habit_id: str
    habit_name: str
    category: str
    completed_count: int
    target_count: int
    completion_rate: float
    weight: int
    weighted_contribution: float
    is_below_threshold: bool


class ScoreExplanation(BaseModel):
    """Why score changed"""
    icon: str  # emoji
    message: str
    impact: float  # points change


class WeeklyAnalytics(BaseModel):
    """Weekly performance breakdown"""
    week_start: date
    week_end: date
    completion_rate: float
    weighted_score: float
    consistency_score: float
    total_completed: int
    total_possible: int
    habit_breakdown: list[HabitBreakdown]
    insights: list[ScoreExplanation]
    daily_rates: list[float]  # 7 values for each day
    comparison_to_last_week: Optional[float] = None


class MonthlyAnalytics(BaseModel):
    """Monthly performance summary"""
    month: int
    year: int
    avg_completion_rate: float
    avg_weighted_score: float
    consistency_trend: float
    performance_grade: str
    top_habits: list[HabitBreakdown]
    struggling_habits: list[HabitBreakdown]
    weekly_scores: list[float]
    score_explanation: list[ScoreExplanation]


class TrendData(BaseModel):
    """Long-term trend data"""
    period: str  # "weekly" or "monthly"
    labels: list[str]
    completion_rates: list[float]
    weighted_scores: list[float]
    consistency_scores: list[float]
