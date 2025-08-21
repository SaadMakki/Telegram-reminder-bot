from apscheduler.schedulers.background import BackgroundScheduler
from .database import db
from .questions import get_question_text, get_question_type, get_question_options
from .utils import create_keyboard
from .config import config
from telebot import TeleBot
import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler()

def setup_scheduler(bot: TeleBot):
    """Initialize and start scheduler jobs."""
    # Job to send scheduled questions
    scheduler.add_job(
        lambda: send_scheduled_questions(bot),
        'interval',
        minutes=config.QUESTION_CHECK_INTERVAL
    )
    
    # Job to send reminders for unanswered questions
    scheduler.add_job(
        lambda: send_reminders(bot),
        'interval',
        hours=config.REMINDER_CHECK_INTERVAL
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started with question check interval: %s minutes, reminder interval: %s hours",
                config.QUESTION_CHECK_INTERVAL, config.REMINDER_CHECK_INTERVAL)

def send_scheduled_questions(bot: TeleBot):
    """Send due questions to users."""
    try:
        # Get questions that are due to be sent
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
                # Send the question to the user
                bot.send_message(
                    user_id, 
                    text, 
                    reply_markup=create_keyboard(qtype, options)
                )
                
                # Mark the question as sent
                db.execute(
                    "UPDATE scheduled_questions SET sent = TRUE, sent_time = NOW() WHERE schedule_id = %s",
                    (schedule_id,)
                )
                logger.info("Sent question %s to user %s", question_id, user_id)
                
    except Exception as e:
        logger.error("Error sending questions: %s", e)

def send_reminders(bot: TeleBot):
    """Send reminders for unanswered questions."""
    try:
        # Get unanswered questions that were sent more than 24 hours ago
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
                # Send reminder for the unanswered question
                bot.send_message(
                    user_id, 
                    f"REMINDER: {text}", 
                    reply_markup=create_keyboard(
                        get_question_type(question_id),
                        get_question_options(question_id)
                    )
                )
                logger.info("Sent reminder for question %s to user %s", question_id, user_id)
                
    except Exception as e:
        logger.error("Error sending reminders: %s", e)