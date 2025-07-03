from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database import Database
from bot.services.weather import WeatherService
from config import OPENWEATHER_API_KEY

router = Router()
db = Database()
weather_service = WeatherService(OPENWEATHER_API_KEY)

@router.callback_query(lambda c: c.data == "weather")
async def weather_callback(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if not user or not user['city']:
        await callback.message.answer("Сначала установите город через кнопку 'Мой город'")
        return
    
    if weather_data := await weather_service.get_weather(user['city']):
        temp, condition = weather_data
        db.add_weather_record(user['user_id'], user['city'], temp, condition)
        await callback.message.answer(f"Погода в {user['city']}: {temp}°C, {condition}")
    else:
        await callback.message.answer("Не удалось получить погоду. Попробуйте позже.")

@router.callback_query(lambda c: c.data == "set_city")
async def ask_city(callback: CallbackQuery):
    await callback.message.answer("Введите название вашего города:")

@router.message(Command("weather"))
@router.message(lambda message: message.text and not message.text.startswith("/"))
async def handle_city(message: Message):
    user_id = message.from_user.id
    city = message.text.strip()
    
    if db.update_city(user_id, city):
        if weather_data := await weather_service.get_weather(city):
            temp, condition = weather_data
            db.add_weather_record(user_id, city, temp, condition)
            await message.answer(f"Город сохранён!\nПогода в {city}: {temp}°C, {condition}")
        else:
            await message.answer("Город сохранён, но не удалось получить погоду")
    else:
        await message.answer("Ошибка при сохранении города")