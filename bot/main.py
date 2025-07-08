import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from config import BOT_TOKEN, OPENWEATHER_API_KEY
from bot.handlers.base import router as base_router
from bot.handlers.weather import router as weather_router
from bot.handlers.profile import router as profile_router
from bot.database import Database
from bot.services.weather import WeatherService
from bot.scheduler import run_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

#async def send_daily_weather(user_id: int, city: str):
#    """Send personalized weather notification"""
#    db = Database()
#    weather_service = WeatherService(OPENWEATHER_API_KEY)
#    bot = Bot(token=BOT_TOKEN)
#    
#    try:
#        logger.info(f"Sending weather to {user_id} for {city}")
#        
#        if weather_data := await weather_service.get_weather(city):
#            temp, condition, timezone = weather_data
#            user_time = datetime.now().strftime("%H:%M")
#            
#            await bot.send_message(
#                user_id,
#                f"🌅 Доброе утро! ({user_time})\n"
#                f"Погода в {city}:\n"
#                f"🌡 {temp}°C, {condition}\n"
#                f"⏰ Часовой пояс: UTC{timezone//3600:+d}"
#            )
#            db.add_weather_record(user_id, city, temp, condition)
#        else:
#            logger.error(f"Weather data not found for {city}")
#            
#    except Exception as e:
#        logger.error(f"Error sending to {user_id}: {str(e)}")
#        await bot.session.close()
#        db.close()

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Include routers
    dp.include_router(base_router)
    dp.include_router(weather_router)
    dp.include_router(profile_router)
    
    # Start scheduler in background
    scheduler_task = asyncio.create_task(run_scheduler())
    
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}")
    finally:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()
        logger.info("Bot stopped gracefully")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")