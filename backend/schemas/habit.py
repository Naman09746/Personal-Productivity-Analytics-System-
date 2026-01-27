"""
Habit schemas
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default="general", max_length=50)
    is_physical: bool = False
    target_per_week: int = Field(default=7, ge=1, le=7)
    weight: int = Field(default=5, ge=1, le=10)
    goal_threshold: int = Field(default=80, ge=0, le=100)


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    is_physical: Optional[bool] = None
    target_per_week: Optional[int] = Field(None, ge=1, le=7)
    weight: Optional[int] = Field(None, ge=1, le=10)
    goal_threshold: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class HabitResponse(BaseModel):
    id: UUID
    name: str
    category: str
    is_physical: bool
    target_per_week: int
    weight: int
    goal_threshold: int
    is_active: bool
    display_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class HabitWithStats(HabitResponse):
    """Habit with current week stats"""
    current_week_completed: int = 0
    current_week_rate: float = 0.0
    is_below_threshold: bool = False
