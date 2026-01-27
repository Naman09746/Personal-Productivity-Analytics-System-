"""
Entries router - Daily habit entries
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import date, timedelta
from typing import List

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.habit import Habit
from models.entry import DailyEntry
from schemas.entry import EntryCreate, EntryUpdate, EntryResponse, DayEntriesResponse, HabitEntryStatus
from services.rule_engine import RuleEngine

router = APIRouter(prefix="/entries", tags=["Entries"])


@router.get("/today", response_model=DayEntriesResponse)
async def get_today_entries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all habit entries for today"""
    return await _get_day_entries(db, current_user.id, date.today())


@router.get("/date/{entry_date}", response_model=DayEntriesResponse)
async def get_date_entries(
    entry_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all habit entries for a specific date"""
    return await _get_day_entries(db, current_user.id, entry_date)


@router.get("/week/{week_start}", response_model=List[DayEntriesResponse])
async def get_week_entries(
    week_start: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all entries for a week (starting from week_start)"""
    days = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_entries = await _get_day_entries(db, current_user.id, day)
        days.append(day_entries)
    return days


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_entry(
    entry_data: EntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a daily entry"""
    # Validate against rules
    await RuleEngine.validate_entry(
        db, 
        current_user.id, 
        entry_data.habit_id, 
        entry_data.entry_date
    )
    
    # Check for existing entry
    existing = await RuleEngine.check_duplicate_entry(
        db, 
        current_user.id, 
        entry_data.habit_id, 
        entry_data.entry_date
    )
    
    if existing:
        # Update existing entry
        existing.completed = entry_data.completed
        if entry_data.notes is not None:
            existing.notes = entry_data.notes
        await db.flush()
        await db.refresh(existing)
        return existing
    
    # Create new entry
    entry = DailyEntry(
        user_id=current_user.id,
        habit_id=entry_data.habit_id,
        entry_date=entry_data.entry_date,
        completed=entry_data.completed,
        notes=entry_data.notes
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: UUID,
    entry_data: EntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing entry"""
    result = await db.execute(
        select(DailyEntry).where(
            and_(DailyEntry.id == entry_id, DailyEntry.user_id == current_user.id)
        )
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    if entry_data.completed is not None:
        entry.completed = entry_data.completed
    if entry_data.notes is not None:
        entry.notes = entry_data.notes
    
    await db.flush()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an entry"""
    result = await db.execute(
        select(DailyEntry).where(
            and_(DailyEntry.id == entry_id, DailyEntry.user_id == current_user.id)
        )
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    await db.delete(entry)
    await db.flush()


async def _get_day_entries(
    db: AsyncSession,
    user_id: UUID,
    target_date: date
) -> DayEntriesResponse:
    """Get all habit statuses for a specific day"""
    # Get active habits
    habits_result = await db.execute(
        select(Habit)
        .where(and_(Habit.user_id == user_id, Habit.is_active == True))
        .order_by(Habit.display_order)
    )
    habits = habits_result.scalars().all()
    
    # Get entries for the date
    entries_result = await db.execute(
        select(DailyEntry).where(
            and_(
                DailyEntry.user_id == user_id,
                DailyEntry.entry_date == target_date
            )
        )
    )
    entries = {e.habit_id: e for e in entries_result.scalars().all()}
    
    # Build response
    habit_statuses = []
    completion_count = 0
    physical_completed = False
    
    for habit in habits:
        entry = entries.get(habit.id)
        completed = entry.completed if entry else False
        
        if completed:
            completion_count += 1
            if habit.is_physical:
                physical_completed = True
        
        habit_statuses.append(HabitEntryStatus(
            habit_id=habit.id,
            habit_name=habit.name,
            category=habit.category,
            is_physical=habit.is_physical,
            completed=completed,
            entry_id=entry.id if entry else None,
            notes=entry.notes if entry else None
        ))
    
    total = len(habits)
    rate = (completion_count / total * 100) if total > 0 else 0
    
    return DayEntriesResponse(
        date=target_date,
        habits=habit_statuses,
        completion_count=completion_count,
        total_habits=total,
        completion_rate=round(rate, 1),
        physical_completed=physical_completed
    )
