"""
Personal Productivity Analytics System - Main Application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routers import auth_router, habits_router, entries_router, analytics_router
from middleware import setup_error_handlers, setup_rate_limiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PPAS...")
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
    
    # Start scheduler in background (non-blocking)
    try:
        from services.scheduler import setup_scheduler
        setup_scheduler()
        logger.info("Scheduler started")
    except Exception as e:
        logger.warning(f"Scheduler init failed: {e}")
    
    yield
    
    # Shutdown
    try:
        from services.scheduler import shutdown_scheduler
        shutdown_scheduler()
    except Exception:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Data-driven habit tracking platform",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
setup_error_handlers(app)
setup_rate_limiter(app)

app.include_router(auth_router, prefix="/api")
app.include_router(habits_router, prefix="/api")
app.include_router(entries_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}


@app.get("/")
async def root():
    return {"message": "PPAS API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
