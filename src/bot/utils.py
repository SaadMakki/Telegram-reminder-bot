from datetime import datetime, timedelta
from telebot import types

def create_keyboard(question_type, options=None):
    """
    Create a reply keyboard based on question type.
    
    Args:
        question_type (str): Type of question ('yes_no' or 'multiple_choice')
        options (list): List of options for multiple choice questions
        
    Returns:
        ReplyKeyboardMarkup: Keyboard markup for the question
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    
    if question_type == 'yes_no':
        markup.add("Yes", "No")
    elif question_type == 'multiple_choice' and options:
        # Add each option as a separate button
        for option in options:
            markup.add(option)
    
    return markup

def get_package_options():
    """Create package selection keyboard."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("1 month")
    markup.add("2 months")
    markup.add("3 months")
    return markup

def schedule_questions(user_group_id, group_id):
    """
    Schedule all questions for a user group.
    
    Args:
        user_group_id (int): ID of the user-group association
        group_id (int): ID of the question group
    """
    from .database import db
    
    # Get questions for this group
    questions = db.execute(
        "SELECT question_id, interval_days, delay_days FROM questions WHERE group_id = %s",
        (group_id,),
        fetch=True
    )
    
    # Get group duration
    duration_result = db.execute(
        "SELECT duration_days FROM question_groups WHERE group_id = %s",
        (group_id,),
        fetch=True
    )
    duration = duration_result[0]['duration_days'] if duration_result else 30
    
    # Get start date
    start_date_result = db.execute(
        "SELECT start_date FROM user_groups WHERE user_group_id = %s",
        (user_group_id,),
        fetch=True
    )
    start_date = start_date_result[0]['start_date'] if start_date_result else datetime.now()
    
    # Generate schedule for each question
    for question in questions:
        question_id = question['question_id']
        interval = question['interval_days']
        delay = question['delay_days']
        
        # Calculate first occurrence
        current_date = start_date + timedelta(days=delay)
        end_date = start_date + timedelta(days=duration)
        
        # Schedule recurring questions until end date
        while current_date <= end_date:
            db.execute(
                "INSERT INTO scheduled_questions (user_group_id, question_id, scheduled_time) VALUES (%s, %s, %s)",
                (user_group_id, question_id, current_date)
            )
            current_date += timedelta(days=interval)