import asyncio
import logging
import sys
from pathlib import Path

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def send_daily_weather():
    """Send daily weather notifications"""
    db = Database()
    weather_service = WeatherService(OPENWEATHER_API_KEY)
    bot = Bot(token=BOT_TOKEN)
    
    try:
        for user_id, city in db.get_users_for_notifications():
            try:
                if weather_data := await weather_service.get_weather(city):
                    temp, condition = weather_data
                    await bot.send_message(
                        user_id,
                        f"🌅 Доброе утро! Погода в {city}:\n"
                        f"🌡 {temp}°C, {condition}"
                    )
                    db.add_weather_record(user_id, city, temp, condition)
            except Exception as e:
                logger.error(f"Error sending to {user_id}: {e}")
    except Exception as e:
        logger.error(f"Daily weather error: {e}")
    finally:
        await bot.session.close()
        db.close()

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Include routers
    dp.include_router(base_router)
    dp.include_router(weather_router)
    dp.include_router(profile_router)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())