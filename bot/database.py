import sqlite3
import logging
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "bot.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables"""
        try:
            self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    city TEXT DEFAULT 'Москва',
                    send_daily BOOLEAN DEFAULT FALSE,
                    timezone TEXT DEFAULT 'Europe/Moscow',
                    timezone_offset INT DEFAULT 10800,                  
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS weather_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    city TEXT,
                    date TEXT,
                    temperature REAL,
                    condition TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def add_user(self, user_id: int, username: str) -> None:
        """Add new user to database"""
        try:
            with self.conn:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                    (user_id, username)
                )
        except sqlite3.Error as e:
            logger.error(f"Error adding user: {e}")
            raise

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            self.cursor.execute(
                "SELECT * FROM users WHERE user_id = ?", 
                (user_id,)
            )
            if row := self.cursor.fetchone():
                return dict(row)
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting user: {e}")
            raise

    def update_city(self, user_id: int, city: str, timezone: int) -> bool:
        """Update user's city"""
        try:
            with self.conn:
                self.cursor.execute(
                    "UPDATE users SET city = ?, timezone_offset = ? WHERE user_id = ?",
                    (city, timezone, user_id)
                )
                return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating city: {e}")
            raise

    def toggle_daily_notifications(self, user_id: int) -> bool:
        """Toggle daily weather notifications"""
        try:
            with self.conn:
                self.cursor.execute(
                    "UPDATE users SET send_daily = NOT send_daily WHERE user_id = ? RETURNING send_daily",
                    (user_id,)
                )
                if row := self.cursor.fetchone():
                    return bool(row[0])
                return False
        except sqlite3.Error as e:
            logger.error(f"Error toggling notifications: {e}")
            raise

    def add_weather_record(self, user_id: int, city: str, temp: float, condition: str) -> None:
        """Add weather record to history"""
        try:
            with self.conn:
                self.cursor.execute(
                    """INSERT INTO weather_history 
                    (user_id, city, date, temperature, condition) 
                    VALUES (?, ?, datetime('now'), ?, ?)""",
                    (user_id, city, temp, condition)
                )
        except sqlite3.Error as e:
            logger.error(f"Error adding weather record: {e}")
            raise

    def get_user_timezone(self, user_id: int) -> int:
        """Возвращает часовой пояс пользователя в формате 'Europe/Moscow'."""
        try:
           self.cursor.execute(
               "SELECT timezone_offset FROM users WHERE user_id = ?", (user_id,)
           )
           return [(row['timezone_offset']) for row in self.cursor.fetchall()]
        
        except sqlite3.Error as e:
            logger.error(f"Error getting users for notifications: {e}")
            raise

    def get_users_for_notifications(self) -> List[Tuple[int, str]]:
        """Get users who enabled daily notifications"""
        try:
            self.cursor.execute(
                "SELECT user_id, city, timezone_offset FROM users WHERE send_daily = TRUE"
            )
            return [(row['user_id'], row['city'], row['timezone_offset']) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting users for notifications: {e}")
            raise

    def close(self) -> None:
        """Close database connection"""
        self.conn.close()