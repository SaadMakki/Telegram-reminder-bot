from telebot import TeleBot
from bot.config import config
from bot.database import db
from bot.scheduler import setup_scheduler
from bot.handlers import setup_handlers
import threading
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to initialize and run the bot."""
    try:
        # Initialize database
        logger.info("Initializing database...")
        db.create_tables()
        db.init_question_data()
        logger.info("Database initialized successfully")
        
        # Create bot instance
        bot = TeleBot(config.BOT_TOKEN)
        
        # Setup handlers
        setup_handlers(bot)
        
        # Setup scheduler
        setup_scheduler(bot)
        
        # Start bot polling in a separate thread
        def polling_thread():
            logger.info("Starting bot polling...")
            bot.infinity_polling()
        
        # Create and start polling thread
        polling_thread = threading.Thread(target=polling_thread, daemon=True)
        polling_thread.start()
        
        logger.info("Bot started successfully. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        while True:
            pass
            
    except Exception as e:
        logger.error("Error starting bot: %s", e)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

if __name__ == "__main__":
    main()