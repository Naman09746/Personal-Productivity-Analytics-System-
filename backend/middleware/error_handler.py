"""
Centralized error handling
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


def setup_error_handlers(app: FastAPI):
    """Register error handlers with the app"""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(f"AppException: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.code,
                "message": exc.message
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error(f"IntegrityError: {str(exc)}")
        
        # Handle unique constraint violations
        if "unique_user_habit_date" in str(exc):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "DUPLICATE_ENTRY",
                    "message": "An entry already exists for this habit on this date"
                }
            )
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "DATABASE_ERROR",
                "message": "A database constraint was violated"
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )
