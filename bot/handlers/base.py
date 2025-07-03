from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database import Database

router = Router()
db = Database()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    db.add_user(user_id, username)
    
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="🌤 Погода", callback_data="weather"),
        types.InlineKeyboardButton(text="🏙 Мой город", callback_data="set_city"),
        types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        types.InlineKeyboardButton(text="⏰ Автопогода", callback_data="toggle_daily")
    )
    builder.adjust(2, 2)
    
    await message.answer(
        f"Привет, {username}! Я бот для отслеживания погоды.",
        reply_markup=builder.as_markup()
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
📌 Доступные команды:
/start - Начать работу
/help - Справка по командам
/weather - Узнать погоду (или кнопка ниже)
"""
    await message.answer(help_text)