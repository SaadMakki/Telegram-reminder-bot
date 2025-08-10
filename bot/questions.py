from bot.database import db

def get_question_text(question_id):
    """Get question text by ID"""
    result = db.execute(
        "SELECT text FROM questions WHERE question_id = %s",
        (question_id,),
        fetch=True
    )
    return result[0]['text'] if result else None

def get_question_type(question_id):
    """Get question type by ID"""
    result = db.execute(
        "SELECT type FROM questions WHERE question_id = %s",
        (question_id,),
        fetch=True
    )
    return result[0]['type'] if result else None

def get_question_options(question_id):
    """Get question options by ID"""
    result = db.execute(
        "SELECT options FROM questions WHERE question_id = %s",
        (question_id,),
        fetch=True
    )
    return result[0]['options'] if result else None

def get_group_duration(group_id):
    """Get group duration in days"""
    result = db.execute(
        "SELECT duration_days FROM question_groups WHERE group_id = %s",
        (group_id,),
        fetch=True
    )
    return result[0]['duration_days'] if result else None

def get_user_group_id(user_id):
    """Get user's active group ID"""
    result = db.execute(
        """SELECT user_group_id FROM user_groups 
        WHERE user_id = %s ORDER BY start_date DESC LIMIT 1""",
        (user_id,),
        fetch=True
    )
    return result[0]['user_group_id'] if result else None