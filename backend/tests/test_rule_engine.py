"""
Rule Engine unit tests
"""
from datetime import date, timedelta
import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from services.rule_engine import RuleEngine, RuleViolation
from models.user import User
from models.habit import Habit
from models.entry import DailyEntry
from services.auth_service import AuthService


@pytest.mark.asyncio
async def test_validate_entry_future_date(db_session: AsyncSession, test_user):
    """Cannot create entries for future dates"""
    habit = Habit(user_id=test_user.id, name="Test", is_physical=False)
    db_session.add(habit)
    await db_session.flush()

    future_date = date.today() + timedelta(days=1)
    with pytest.raises(RuleViolation) as exc:
        await RuleEngine.validate_entry(db_session, test_user.id, habit.id, future_date)
    assert "future" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_validate_entry_one_physical_per_day(db_session: AsyncSession, test_user):
    """Only one physical activity per day"""
    run = Habit(user_id=test_user.id, name="Run", is_physical=True)
    gym = Habit(user_id=test_user.id, name="Gym", is_physical=True)
    db_session.add_all([run, gym])
    await db_session.flush()

    today = date.today()
    await RuleEngine.validate_entry(db_session, test_user.id, run.id, today)

    # First physical - create entry
    entry = DailyEntry(user_id=test_user.id, habit_id=run.id, entry_date=today, completed=True)
    db_session.add(entry)
    await db_session.flush()

    # Second physical same day should fail
    with pytest.raises(RuleViolation) as exc:
        await RuleEngine.validate_entry(db_session, test_user.id, gym.id, today)
    assert "one physical" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_validate_entry_physical_own_habit_allowed(db_session: AsyncSession, test_user):
    """Can update same physical habit entry (toggle off/on)"""
    run = Habit(user_id=test_user.id, name="Run", is_physical=True)
    db_session.add(run)
    await db_session.flush()

    today = date.today()
    await RuleEngine.validate_entry(db_session, test_user.id, run.id, today)
    # Same habit - validation passes (used for update)
    result = await RuleEngine.validate_entry(db_session, test_user.id, run.id, today)
    assert result is True


def test_validate_habit_config_weight():
    """Weight must be 1-10"""
    RuleEngine.validate_habit_config(5, 7, 80)  # OK
    with pytest.raises(RuleViolation):
        RuleEngine.validate_habit_config(0, 7, 80)
    with pytest.raises(RuleViolation):
        RuleEngine.validate_habit_config(11, 7, 80)


def test_validate_habit_config_target():
    """Target per week must be 1-7"""
    RuleEngine.validate_habit_config(5, 5, 80)  # OK
    with pytest.raises(RuleViolation):
        RuleEngine.validate_habit_config(5, 0, 80)
    with pytest.raises(RuleViolation):
        RuleEngine.validate_habit_config(5, 8, 80)


def test_validate_habit_config_threshold():
    """Goal threshold must be 0-100"""
    RuleEngine.validate_habit_config(5, 7, 50)  # OK
    with pytest.raises(RuleViolation):
        RuleEngine.validate_habit_config(5, 7, -1)
    with pytest.raises(RuleViolation):
        RuleEngine.validate_habit_config(5, 7, 101)
