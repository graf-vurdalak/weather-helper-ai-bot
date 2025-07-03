from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging
from bot.main import send_daily_weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def run_scheduler():
    scheduler = AsyncIOScheduler()
    
    # Schedule daily at 8:00 AM
    scheduler.add_job(
        send_daily_weather,
        'cron',
        hour=8,
        minute=0,
        timezone='Europe/Moscow'
    )
    
    scheduler.start()
    logger.info("Scheduler started. Daily weather at 8:00 AM Moscow time")
    
    try:
        await asyncio.Future()  # Run forever
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(run_scheduler())