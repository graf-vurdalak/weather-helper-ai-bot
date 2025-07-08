import logging
from datetime import datetime
from bot.database import Database
from bot.services.weather import WeatherService
from config import BOT_TOKEN, OPENWEATHER_API_KEY
from aiogram import Bot

logger = logging.getLogger(__name__)

async def send_daily_weather(user_id: int, city: str):
    """Send personalized weather notification"""
    db = Database()
    weather_service = WeatherService(OPENWEATHER_API_KEY)
    bot = Bot(token=BOT_TOKEN)
    
    try:
        logger.info(f"Sending weather to {user_id} for {city}")
        
        if weather_data := await weather_service.get_weather(city):
            temp, condition, timezone = weather_data
            user_time = datetime.now().strftime("%H:%M")
            
            await bot.send_message(
                user_id,
                f"🌅 Доброе утро! ({user_time})\n"
                f"Погода в {city}:\n"
                f"🌡 {temp}°C, {condition}\n"
                f"⏰ Часовой пояс: UTC{timezone//3600:+d}"
            )
            db.add_weather_record(user_id, city, temp, condition)
        else:
            logger.error(f"Weather data not found for {city}")
            
    except Exception as e:
        logger.error(f"Error sending to {user_id}: {str(e)}")
    finally:
        await bot.session.close()
        db.close()
