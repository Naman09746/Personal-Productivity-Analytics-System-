"""
Entries API tests
"""
from datetime import date
import pytest
from httpx import AsyncClient

from models.habit import Habit


@pytest.mark.asyncio
async def test_create_entry(client: AsyncClient, auth_headers, test_user, db_session):
    """Create entry succeeds"""
    habit = Habit(user_id=test_user.id, name="Read", is_physical=False)
    db_session.add(habit)
    await db_session.flush()

    resp = await client.post("/api/entries", json={
        "habit_id": str(habit.id),
        "entry_date": date.today().isoformat(),
        "completed": True
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["completed"] is True
    assert data["habit_id"] == str(habit.id)
    assert data["entry_date"] == date.today().isoformat()


@pytest.mark.asyncio
async def test_create_entry_future_date(client: AsyncClient, auth_headers, test_user, db_session):
    """Create entry for future date fails"""
    habit = Habit(user_id=test_user.id, name="Read", is_physical=False)
    db_session.add(habit)
    await db_session.flush()

    from datetime import timedelta
    future = (date.today() + timedelta(days=1)).isoformat()
    resp = await client.post("/api/entries", json={
        "habit_id": str(habit.id),
        "entry_date": future,
        "completed": True
    }, headers=auth_headers)
    assert resp.status_code == 400
    assert "future" in resp.json().get("message", "").lower() or "future" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_or_update_entry_upsert(client: AsyncClient, auth_headers, test_user, db_session):
    """Same habit/date updates existing entry"""
    habit = Habit(user_id=test_user.id, name="Meditate", is_physical=False)
    db_session.add(habit)
    await db_session.flush()

    today = date.today().isoformat()
    # First call - create
    r1 = await client.post("/api/entries", json={
        "habit_id": str(habit.id),
        "entry_date": today,
        "completed": True
    }, headers=auth_headers)
    assert r1.status_code == 201
    entry_id = r1.json()["id"]

    # Second call - update (toggle off)
    r2 = await client.post("/api/entries", json={
        "habit_id": str(habit.id),
        "entry_date": today,
        "completed": False
    }, headers=auth_headers)
    assert r2.status_code == 201
    assert r2.json()["id"] == entry_id
    assert r2.json()["completed"] is False


@pytest.mark.asyncio
async def test_get_today_entries(client: AsyncClient, auth_headers, test_user, db_session):
    """GET /entries/today returns day structure"""
    habit = Habit(user_id=test_user.id, name="Exercise", is_physical=True)
    db_session.add(habit)
    await db_session.flush()

    resp = await client.get("/api/entries/today", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "habits" in data
    assert data["date"] == date.today().isoformat()
    assert data["total_habits"] >= 0
    assert "completion_rate" in data
