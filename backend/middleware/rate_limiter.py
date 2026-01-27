"""
Rate limiting middleware using SlowAPI
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

from config import settings

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiter(app: FastAPI):
    """Setup rate limiting for the app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Decorator for rate limiting specific endpoints
# Usage: @limiter.limit("100/minute")
