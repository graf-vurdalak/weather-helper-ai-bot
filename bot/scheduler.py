from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging
from bot.tasks import send_daily_weather
from bot.database import Database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scheduler.log")  # Логи в отдельный файл
    ]
)
logger = logging.getLogger(__name__)

async def run_scheduler():
    """Основная функция запуска планировщика"""
    try:
        scheduler = AsyncIOScheduler()
        db = Database()
        
        # Получаем пользователей с включенными уведомлениями
        users = db.get_users_for_notifications()
        if not users:
            logger.warning("No users with enabled notifications found")
            return
        
        logger.info(f"Found {len(users)} users with enabled notifications")
        
        for user_id, city, timezone_offset in users:
            try:
                # Конвертируем смещение в формат для APScheduler
                gmt_offset = -(timezone_offset // 3600)
                timezone_str = f"Etc/GMT{gmt_offset}"
                
                logger.debug(f"Adding job for user {user_id} (city: {city}, tz: {timezone_str})")
                
                scheduler.add_job(
                    send_daily_weather,
                    'cron',
                    hour=9,
                    minute=0,
                    kwargs={'user_id': user_id, 'city': city},
                    timezone=timezone_str,
                    misfire_grace_time=3600  # Допустимое время задержки (1 час)
                )
                
            except Exception as e:
                logger.error(f"Failed to schedule for user {user_id}: {str(e)}")
                continue
        
        scheduler.start()
        logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))
        
        # Бесконечный цикл для работы планировщика
        while True:
            await asyncio.sleep(3600)  # Проверка каждые 1 час
            
    except Exception as e:
        logger.critical(f"Scheduler crashed: {str(e)}")
        raise
    finally:
        if 'scheduler' in locals() and scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped gracefully")

if __name__ == "__main__":
    try:
        asyncio.run(run_scheduler())
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.critical(f"Fatal scheduler error: {str(e)}")