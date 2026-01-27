"""
Entry schemas
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class EntryCreate(BaseModel):
    habit_id: UUID
    entry_date: date
    completed: bool = True
    notes: Optional[str] = Field(None, max_length=500)


class EntryUpdate(BaseModel):
    completed: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class EntryResponse(BaseModel):
    id: UUID
    habit_id: UUID
    entry_date: date
    completed: bool
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class HabitEntryStatus(BaseModel):
    """Status of a habit for a specific day"""
    habit_id: UUID
    habit_name: str
    category: str
    is_physical: bool
    completed: bool
    entry_id: Optional[UUID] = None
    notes: Optional[str] = None


class DayEntriesResponse(BaseModel):
    """All entries for a specific day"""
    date: date
    habits: list[HabitEntryStatus]
    completion_count: int
    total_habits: int
    completion_rate: float
    physical_completed: bool = False
