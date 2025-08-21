import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Telegram bot application."""
    
    # Telegram Bot Token from environment variables
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # PostgreSQL Database Configuration
    DB_NAME = os.getenv("DB_NAME", "telegram_bot")
    DB_USER = os.getenv("DB_USER", "bot_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    # Scheduler Settings
    QUESTION_CHECK_INTERVAL = int(os.getenv("QUESTION_CHECK_INTERVAL", 5))  # minutes
    REMINDER_CHECK_INTERVAL = int(os.getenv("REMINDER_CHECK_INTERVAL", 24))  # hours

    @property
    def DB_CONFIG(self):
        """Return database configuration as a dictionary."""
        return {
            "dbname": self.DB_NAME,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "host": self.DB_HOST,
            "port": self.DB_PORT
        }

# Create a global configuration instance
config = Config()