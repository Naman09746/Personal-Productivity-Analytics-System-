"""
Habits router - CRUD for user habits
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from typing import List

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.habit import Habit
from schemas.habit import HabitCreate, HabitUpdate, HabitResponse

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.get("", response_model=List[HabitResponse])
async def list_habits(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all habits for current user"""
    query = select(Habit).where(Habit.user_id == current_user.id)
    if active_only:
        query = query.where(Habit.is_active == True)
    query = query.order_by(Habit.display_order, Habit.created_at)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_data: HabitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new habit"""
    # Get max display order
    result = await db.execute(
        select(Habit.display_order)
        .where(Habit.user_id == current_user.id)
        .order_by(Habit.display_order.desc())
        .limit(1)
    )
    max_order = result.scalar() or 0
    
    habit = Habit(
        user_id=current_user.id,
        name=habit_data.name,
        category=habit_data.category,
        is_physical=habit_data.is_physical,
        target_per_week=habit_data.target_per_week,
        weight=habit_data.weight,
        goal_threshold=habit_data.goal_threshold,
        display_order=max_order + 1
    )
    db.add(habit)
    await db.flush()
    await db.refresh(habit)
    return habit


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific habit"""
    result = await db.execute(
        select(Habit).where(
            and_(Habit.id == habit_id, Habit.user_id == current_user.id)
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    return habit


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: UUID,
    habit_data: HabitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a habit"""
    result = await db.execute(
        select(Habit).where(
            and_(Habit.id == habit_id, Habit.user_id == current_user.id)
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Update fields
    update_data = habit_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    await db.flush()
    await db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate a habit (soft delete)"""
    result = await db.execute(
        select(Habit).where(
            and_(Habit.id == habit_id, Habit.user_id == current_user.id)
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    habit.is_active = False
    await db.flush()


@router.post("/{habit_id}/reorder")
async def reorder_habit(
    habit_id: UUID,
    new_order: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change display order of a habit"""
    result = await db.execute(
        select(Habit).where(
            and_(Habit.id == habit_id, Habit.user_id == current_user.id)
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    habit.display_order = new_order
    await db.flush()
    return {"message": "Order updated", "new_order": new_order}
