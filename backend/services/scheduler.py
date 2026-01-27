"""
Background job scheduler using APScheduler
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

scheduler = None


def setup_scheduler():
    """Configure and start the scheduler"""
    global scheduler
    try:
        scheduler = AsyncIOScheduler()
        # Jobs will be added when scheduler is actually needed
        # For now, just initialize without adding jobs to avoid blocking
        scheduler.start()
        logger.info("Background scheduler started")
    except Exception as e:
        logger.warning(f"Scheduler could not be started: {e}")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    global scheduler
    if scheduler:
        try:
            scheduler.shutdown()
            logger.info("Background scheduler stopped")
        except Exception:
            pass
