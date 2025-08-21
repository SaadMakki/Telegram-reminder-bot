from telebot import TeleBot, types
from .database import db
from .utils import create_keyboard, get_package_options, schedule_questions
from .config import config
import datetime

# Dictionary to track user states during conversations
user_states = {}

def setup_handlers(bot: TeleBot):
    """Setup all message handlers for the bot."""
    
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        """Handle the /start command to begin interaction with user."""
        user_id = message.chat.id
        bot.send_message(user_id, "Hello! Please enter your name:")
        user_states[user_id] = {"state": "awaiting_name"}
    
    @bot.message_handler(commands=['help'])
    def help_handler(message):
        """Handle the /help command to provide assistance."""
        help_text = """
        Welcome to the Reminder Bot!
        
        Available commands:
        /start - Begin using the bot
        /help - Show this help message
        
        This bot will send you regular questions based on your selected package.
        Please answer them when they appear to help us track your progress.
        """
        bot.send_message(message.chat.id, help_text)

    @bot.message_handler(func=lambda message: True)
    def message_handler(message):
        """Handle all text messages based on user state."""
        user_id = message.chat.id
        text = message.text.strip()
        
        # If user is not in state tracking, start conversation
        if user_id not in user_states:
            start_handler(message)
            return
            
        state = user_states[user_id].get("state")
        
        # Route to appropriate handler based on state
        if state == "awaiting_name":
            handle_name(bot, user_id, text)
        elif state == "awaiting_package":
            handle_package(bot, user_id, text)
        else:
            handle_answer(bot, user_id, text)

def handle_name(bot, user_id, name):
    """Process user's name and save to database."""
    # Get username if available
    chat = bot.get_chat(user_id)
    username = f"@{chat.username}" if chat.username else None
    
    # Save or update user in database
    db.execute(
        """INSERT INTO users (user_id, username, full_name, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
        full_name = EXCLUDED.full_name, username = EXCLUDED.username""",
        (user_id, username, name, datetime.datetime.now())
    )
    
    # Move to package selection state
    user_states[user_id] = {"state": "awaiting_package", "name": name}
    bot.send_message(
        user_id, 
        "Please select a package:", 
        reply_markup=get_package_options()
    )

def handle_package(bot, user_id, package):
    """Process user's package selection and schedule questions."""
    valid_packages = ["1 month", "2 months", "3 months"]
    
    # Validate package selection
    if package not in valid_packages:
        bot.send_message(
            user_id, 
            "Invalid selection. Please choose a package:", 
            reply_markup=get_package_options()
        )
        return
    
    # Map package name to group ID
    package_to_group = {
        "1 month": 1,
        "2 months": 2,
        "3 months": 3
    }
    group_id = package_to_group[package]
    
    # Create user group association
    db.execute(
        """INSERT INTO user_groups (user_id, group_id, start_date)
        VALUES (%s, %s, %s)""",
        (user_id, group_id, datetime.datetime.now())
    )
    
    # Get the newly created user_group_id
    result = db.execute(
        """SELECT user_group_id FROM user_groups 
        WHERE user_id = %s ORDER BY start_date DESC LIMIT 1""",
        (user_id,),
        fetch=True
    )
    user_group_id = result[0]['user_group_id'] if result else None
    
    # Schedule questions for this user
    if user_group_id:
        schedule_questions(user_group_id, group_id)
    
    # Send confirmation message
    user_name = user_states[user_id].get('name', 'user')
    bot.send_message(
        user_id, 
        f"Hello, {user_name}!\nYou have registered for: {package}",
        reply_markup=types.ReplyKeyboardRemove()
    )
    
    # Clean up state
    del user_states[user_id]

def handle_answer(bot, user_id, answer):
    """Process user's answer to a question."""
    # Find the latest pending question for this user
    result = db.execute(
        """SELECT sq.schedule_id, q.type, q.options
        FROM scheduled_questions sq
        JOIN user_groups ug ON sq.user_group_id = ug.user_group_id
        JOIN questions q ON sq.question_id = q.question_id
        WHERE ug.user_id = %s 
        AND sq.sent = TRUE 
        AND NOT EXISTS (
            SELECT 1 FROM user_answers ua
            WHERE ua.schedule_id = sq.schedule_id
        )
        ORDER BY sq.scheduled_time DESC
        LIMIT 1""",
        (user_id,),
        fetch=True
    )
    
    if result:
        schedule_id = result[0]['schedule_id']
        qtype = result[0]['type']
        options = result[0]['options']
        
        # Validate answer based on question type
        valid_answers = []
        if qtype == 'yes_no':
            valid_answers = ["Yes", "No"]
        elif options:
            valid_answers = options
            
        if valid_answers and answer not in valid_answers:
            bot.send_message(
                user_id, 
                f"Invalid answer. Please choose one of the following options:",
                reply_markup=create_keyboard(qtype, options)
            )
            return
        
        # Save the valid answer
        db.execute(
            "INSERT INTO user_answers (schedule_id, answer) VALUES (%s, %s)",
            (schedule_id, answer)
        )
        
        bot.send_message(
            user_id, 
            "Your answer has been saved!", 
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        bot.send_message(user_id, "You don't have any questions to answer right now.")