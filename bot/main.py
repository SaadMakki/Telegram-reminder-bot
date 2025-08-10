from telebot import TeleBot
from bot.config import config
from bot.database import db
from bot.scheduler import setup_scheduler
from bot.handlers import setup_handlers
import threading

def main():
    # Initialize database
    db.create_tables()
    db.init_question_data()
    
    # Create bot instance
    bot = TeleBot(config.BOT_TOKEN)
    
    # Setup handlers
    setup_handlers(bot)
    
    # Setup scheduler
    setup_scheduler(bot)
    
    # Start bot polling in a separate thread
    def polling_thread():
        bot.infinity_polling()
    
    threading.Thread(target=polling_thread, daemon=True).start()
    
    # Keep main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Bot stopped")

if __name__ == "__main__":
    main()