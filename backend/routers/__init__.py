"""Routers package"""
from routers.auth import router as auth_router
from routers.habits import router as habits_router
from routers.entries import router as entries_router
from routers.analytics import router as analytics_router

__all__ = ["auth_router", "habits_router", "entries_router", "analytics_router"]
