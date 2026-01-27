"""
Middleware package
"""
from middleware.error_handler import setup_error_handlers
from middleware.rate_limiter import limiter, setup_rate_limiter

__all__ = ["setup_error_handlers", "limiter", "setup_rate_limiter"]
