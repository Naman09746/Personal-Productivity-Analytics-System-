"""
Rule Engine - Business rules enforcement
"""
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from models.habit import Habit
from models.entry import DailyEntry


class RuleViolation(HTTPException):
    """Custom exception for rule violations"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class RuleEngine:
    """Enforces business rules for habit tracking"""
    
    @staticmethod
    async def validate_entry(
        db: AsyncSession,
        user_id: UUID,
        habit_id: UUID,
        entry_date: date
    ) -> bool:
        """
        Validate a new entry against all business rules.
        
        Rules:
        1. Entry date cannot be in the future
        2. Only one physical activity can be completed per day
        """
        # Rule 1: No future entries
        if entry_date > date.today():
            raise RuleViolation("Cannot create entries for future dates")
        
        # Get the habit
        result = await db.execute(
            select(Habit).where(
                and_(Habit.id == habit_id, Habit.user_id == user_id)
            )
        )
        habit = result.scalar_one_or_none()
        
        if not habit:
            raise RuleViolation("Habit not found")
        
        if not habit.is_active:
            raise RuleViolation("Cannot log entries for inactive habits")
        
        # Rule 2: One physical activity per day
        if habit.is_physical:
            existing_physical = await RuleEngine.get_physical_entry_for_date(
                db, user_id, entry_date
            )
            if existing_physical and existing_physical.habit_id != habit_id:
                raise RuleViolation(
                    "Only one physical activity can be completed per day. "
                    f"You already completed '{existing_physical.habit.name}' today."
                )
        
        return True
    
    @staticmethod
    async def get_physical_entry_for_date(
        db: AsyncSession,
        user_id: UUID,
        entry_date: date
    ) -> DailyEntry | None:
        """Get completed physical activity entry for a date"""
        result = await db.execute(
            select(DailyEntry)
            .join(Habit)
            .where(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.entry_date == entry_date,
                    DailyEntry.completed == True,
                    Habit.is_physical == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def check_duplicate_entry(
        db: AsyncSession,
        user_id: UUID,
        habit_id: UUID,
        entry_date: date
    ) -> DailyEntry | None:
        """Check if entry already exists for this user/habit/date"""
        result = await db.execute(
            select(DailyEntry).where(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.habit_id == habit_id,
                    DailyEntry.entry_date == entry_date
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    def validate_habit_config(
        weight: int,
        target_per_week: int,
        goal_threshold: int
    ) -> bool:
        """Validate habit configuration values"""
        if not 1 <= weight <= 10:
            raise RuleViolation("Weight must be between 1 and 10")
        if not 1 <= target_per_week <= 7:
            raise RuleViolation("Target per week must be between 1 and 7")
        if not 0 <= goal_threshold <= 100:
            raise RuleViolation("Goal threshold must be between 0 and 100")
        return True
