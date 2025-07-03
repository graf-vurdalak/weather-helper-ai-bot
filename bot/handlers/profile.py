from aiogram import Router, types
from aiogram.types import CallbackQuery

from bot.database import Database

router = Router()
db = Database()

@router.callback_query(lambda c: c.data == "profile")
async def profile_callback(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала запустите /start")
        return
    
    status = "вкл" if user['send_daily'] else "выкл"
    
    text = (
        f"👤 <b>Профиль</b>\n"
        f"├ Имя: {user['username']}\n"
        f"├ Город: {user['city']}\n"
        f"├ Автопогода: {status}\n"
        f"└ Часовой пояс: {user['timezone']}"
    )
    await callback.message.answer(text, parse_mode="HTML")

@router.callback_query(lambda c: c.data == "toggle_daily")
async def toggle_daily(callback: CallbackQuery):
    new_status = db.toggle_daily_notifications(callback.from_user.id)
    status = "включена" if new_status else "выключена"
    await callback.answer(f"Автоматическая погода {status}!")