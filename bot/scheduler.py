from apscheduler.schedulers.background import BackgroundScheduler
from bot.database import db
from bot.questions import get_question_text, get_question_type, get_question_options
from bot.utils import create_keyboard
from bot.config import config
from telebot import TeleBot
import datetime

scheduler = BackgroundScheduler()

def setup_scheduler(bot: TeleBot):
    """Initialize and start scheduler jobs"""
    scheduler.add_job(
        lambda: send_scheduled_questions(bot),
        'interval',
        minutes=config.QUESTION_CHECK_INTERVAL
    )
    
    scheduler.add_job(
        lambda: send_reminders(bot),
        'interval',
        hours=config.REMINDER_CHECK_INTERVAL
    )
    
    scheduler.start()

def send_scheduled_questions(bot: TeleBot):
    """Send due questions to users"""
    try:
        # Get due questions
        results = db.execute(
            """SELECT sq.schedule_id, u.user_id, q.question_id
            FROM scheduled_questions sq
            JOIN user_groups ug ON sq.user_group_id = ug.user_group_id
            JOIN users u ON ug.user_id = u.user_id
            JOIN questions q ON sq.question_id = q.question_id
            WHERE sq.sent = FALSE 
            AND sq.scheduled_time <= NOW()""",
            fetch=True
        )
        
        for row in results:
            schedule_id = row['schedule_id']
            user_id = row['user_id']
            question_id = row['question_id']
            
            # Get question details
            text = get_question_text(question_id)
            qtype = get_question_type(question_id)
            options = get_question_options(question_id)
            
            if text:
                # Send question
                bot.send_message(
                    user_id, 
                    text, 
                    reply_markup=create_keyboard(qtype, options)
                )
                
                # Update schedule
                db.execute(
                    "UPDATE scheduled_questions SET sent = TRUE, sent_time = NOW() WHERE schedule_id = %s",
                    (schedule_id,)
                )
                
    except Exception as e:
        print(f"Error sending questions: {e}")

def send_reminders(bot: TeleBot):
    """Send reminders for unanswered questions"""
    try:
        # Get unanswered questions (older than 24h)
        results = db.execute(
            """SELECT sq.schedule_id, u.user_id, q.question_id
            FROM scheduled_questions sq
            JOIN user_groups ug ON sq.user_group_id = ug.user_group_id
            JOIN users u ON ug.user_id = u.user_id
            JOIN questions q ON sq.question_id = q.question_id
            WHERE sq.sent = TRUE
            AND sq.sent_time < NOW() - INTERVAL '24 HOURS'
            AND NOT EXISTS (
                SELECT 1 FROM user_answers ua
                WHERE ua.schedule_id = sq.schedule_id
            )""",
            fetch=True
        )
        
        for row in results:
            user_id = row['user_id']
            question_id = row['question_id']
            text = get_question_text(question_id)
            
            if text:
                bot.send_message(
                    user_id, 
                    f"ЕСКЕРТУ: {text}", 
                    reply_markup=create_keyboard(
                        get_question_type(question_id),
                        get_question_options(question_id)
                    )
                )
                
    except Exception as e:
        print(f"Error sending reminders: {e}")