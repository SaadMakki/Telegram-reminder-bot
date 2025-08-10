from telebot import TeleBot, types
from bot.database import db
from bot.questions import get_user_group_id
from bot.utils import create_keyboard, get_package_options, schedule_questions
from bot.config import config
import datetime

# User state tracking
user_states = {}

def setup_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        """Handle /start command"""
        user_id = message.chat.id
        bot.send_message(user_id, "Сәлеметсіз бе! Атыңызды енгізіңіз:")
        user_states[user_id] = {"state": "awaiting_name"}

    @bot.message_handler(func=lambda message: True)
    def message_handler(message):
        """Handle all text messages"""
        user_id = message.chat.id
        text = message.text.strip()
        
        if user_id not in user_states:
            start_handler(message)
            return
            
        state = user_states[user_id].get("state")
        
        if state == "awaiting_name":
            handle_name(bot, user_id, text)
        elif state == "awaiting_package":
            handle_package(bot, user_id, text)
        else:
            handle_answer(bot, user_id, text)

def handle_name(bot, user_id, name):
    """Process user's name"""
    # Save user to database
    username = f"@{bot.get_chat(user_id).username}" if bot.get_chat(user_id).username else None
    db.execute(
        """INSERT INTO users (user_id, username, full_name, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
        full_name = EXCLUDED.full_name, username = EXCLUDED.username""",
        (user_id, username, name, datetime.datetime.now())
    )
    
    # Move to next state
    user_states[user_id] = {"state": "awaiting_package"}
    bot.send_message(
        user_id, 
        "Курсты таңдаңыз:", 
        reply_markup=get_package_options()
    )

def handle_package(bot, user_id, package):
    """Process selected package"""
    valid_packages = ["1 айлык", "2 айлык", "3 айлык"]
    
    if package not in valid_packages:
        bot.send_message(
            user_id, 
            "Қате таңдау. Курсты таңдаңыз:", 
            reply_markup=get_package_options()
        )
        return
    
    # Map package to group ID
    package_to_group = {
        "1 айлык": 1,
        "2 айлык": 2,
        "3 айлык": 3
    }
    group_id = package_to_group[package]
    
    # Create user group
    db.execute(
        """INSERT INTO user_groups (user_id, group_id, start_date)
        VALUES (%s, %s, %s)""",
        (user_id, group_id, datetime.datetime.now())
    )
    
    # Get user_group_id
    user_group_id = db.execute(
        """SELECT user_group_id FROM user_groups 
        WHERE user_id = %s ORDER BY start_date DESC LIMIT 1""",
        (user_id,),
        fetch=True
    )[0]['user_group_id']
    
    # Schedule questions
    schedule_questions(user_group_id, group_id)
    
    # Send confirmation
    bot.send_message(
        user_id, 
        f"Сәлем, {user_states[user_id].get('name', 'пайдаланушы')}!\nСіз тіркелген курс: {package}",
        reply_markup=types.ReplyKeyboardRemove()
    )
    del user_states[user_id]

def handle_answer(bot, user_id, answer):
    """Process user's answer to a question"""
    # Find latest pending question
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
        schedule_id, qtype, options = result[0]['schedule_id'], result[0]['type'], result[0]['options']
        
        # Validate answer
        valid_answers = []
        if qtype == 'yes_no':
            valid_answers = ["Иә", "Жоқ"]
        elif options:
            valid_answers = options
            
        if valid_answers and answer not in valid_answers:
            bot.send_message(
                user_id, 
                f"Қате жауап. Төмендегі опциялардың бірін таңдаңыз:",
                reply_markup=create_keyboard(qtype, options)
            )
            return
        
        # Save answer
        db.execute(
            "INSERT INTO user_answers (schedule_id, answer) VALUES (%s, %s)",
            (schedule_id, answer)
        )
        
        bot.send_message(
            user_id, 
            "Жауабыңыз сақталды!", 
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        bot.send_message(user_id, "Сізде жауап беруге тиісті сұрақтар жоқ.")