from datetime import datetime, timedelta
from telebot import types

def create_keyboard(question_type, options=None):
    """Create reply keyboard based on question type"""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    
    if question_type == 'yes_no':
        markup.add("Иә", "Жоқ")
    elif question_type == 'multiple_choice' and options:
        for option in options:
            markup.add(option)
    
    return markup

def get_package_options():
    """Create package selection keyboard"""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("1 айлык")
    markup.add("2 айлык")
    markup.add("3 айлык")
    return markup

def schedule_questions(user_group_id, group_id):
    """Schedule all questions for a user group"""
    from bot.database import db
    
    # Get questions for this group
    questions = db.execute(
        "SELECT question_id, interval_days, delay_days FROM questions WHERE group_id = %s",
        (group_id,),
        fetch=True
    )
    
    # Get group duration
    duration = db.execute(
        "SELECT duration_days FROM question_groups WHERE group_id = %s",
        (group_id,),
        fetch=True
    )[0]['duration_days']
    
    # Get start date
    start_date = db.execute(
        "SELECT start_date FROM user_groups WHERE user_group_id = %s",
        (user_group_id,),
        fetch=True
    )[0]['start_date']
    
    # Generate schedule for each question
    for question in questions:
        question_id, interval, delay = question['question_id'], question['interval_days'], question['delay_days']
        current_date = start_date + timedelta(days=delay)
        end_date = start_date + timedelta(days=duration)
        
        while current_date <= end_date:
            db.execute(
                "INSERT INTO scheduled_questions (user_group_id, question_id, scheduled_time) VALUES (%s, %s, %s)",
                (user_group_id, question_id, current_date)
            )
            current_date += timedelta(days=interval)