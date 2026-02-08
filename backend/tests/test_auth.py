"""
Authentication API tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Register creates user and returns tokens"""
    resp = await client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepass123",
        "name": "New User",
        "timezone": "UTC"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Duplicate email returns 400"""
    payload = {
        "email": "dup@example.com",
        "password": "pass123456",
        "name": "First User"
    }
    await client.post("/api/auth/register", json=payload)
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400
    assert "email" in resp.json().get("detail", "").lower() or "already" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    """Login returns tokens for valid credentials"""
    resp = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    """Login returns 401 for wrong password"""
    resp = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """Login returns 401 for non-existent email"""
    resp = await client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient, auth_headers):
    """GET /me returns current user"""
    resp = await client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient):
    """GET /me returns 401 without token"""
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 403  # HTTPBearer returns 403 for missing auth


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    """Refresh token returns new tokens"""
    login_resp = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
