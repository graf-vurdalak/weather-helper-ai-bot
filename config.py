import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHERMAP_TOKEN")