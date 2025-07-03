import requests
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    async def get_weather(self, city: str) -> Optional[Tuple[float, str]]:
        """Get current weather for city"""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") != 200:
                logger.warning(f"Weather API error: {data.get('message', 'Unknown error')}")
                return None

            temp = data['main']['temp']
            condition = data['weather'][0]['description']
            return temp, condition

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Data parsing error: {e}")
            return None