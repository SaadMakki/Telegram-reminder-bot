# API Reference

This document provides comprehensive API documentation for the Telegram Reminder Bot, including all classes, methods, functions, and their usage examples.

## Table of Contents
- [Configuration Module](#configuration-module)
- [Database Module](#database-module)
- [Handlers Module](#handlers-module)
- [Scheduler Module](#scheduler-module)
- [Questions Module](#questions-module)
- [Utils Module](#utils-module)
- [Main Module](#main-module)
- [Usage Examples](#usage-examples)
- [Error Codes](#error-codes)

## Configuration Module

### `Config` Class

```python
class Config:
    """Configuration management class implementing Singleton pattern."""
```

#### Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `BOT_TOKEN` | `str` | Telegram Bot API token | `None` |
| `DB_NAME` | `str` | Database name | `"telegram_bot"` |
| `DB_USER` | `str` | Database username | `"bot_user"` |
| `DB_PASSWORD` | `str` | Database password | `None` |
| `DB_HOST` | `str` | Database host | `"localhost"` |
| `DB_PORT` | `str` | Database port | `"5432"` |
| `QUESTION_CHECK_INTERVAL` | `int` | Question check interval (minutes) | `5` |
| `REMINDER_CHECK_INTERVAL` | `int` | Reminder check interval (hours) | `24` |

#### Methods

##### `DB_CONFIG`
```python
@property
def DB_CONFIG(self) -> dict:
    """Return database configuration as a dictionary.
    
    Returns:
        dict: Database connection parameters
        
    Example:
        >>> config = Config()
        >>> db_config = config.DB_CONFIG
        >>> print(db_config)
        {
            'dbname': 'telegram_bot',
            'user': 'bot_user',
            'password': 'your_password',
            'host': 'localhost',
            'port': '5432'
        }
    """
```

## Database Module

### `Database` Class

```python
class Database:
    """Database abstraction layer implementing Repository pattern."""
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `conn` | `psycopg2.connection` | PostgreSQL connection object |

#### Methods

##### `__init__()`
```python
def __init__(self):
    """Initialize database connection.
    
    Sets connection to None for lazy initialization.
    """
```

##### `connect()`
```python
def connect(self) -> psycopg2.connection:
    """Establish database connection if not already connected.
    
    Returns:
        psycopg2.connection: Active database connection
        
    Example:
        >>> db = Database()
        >>> conn = db.connect()
        >>> print(conn.status)
        1  # CONNECTION_OK
    """
```

##### `execute()`
```python
def execute(self, query: str, params: tuple = None, fetch: bool = False) -> list | None:
    """Execute SQL query with optional parameters.
    
    Args:
        query (str): SQL query with placeholder parameters
        params (tuple, optional): Parameters for prepared statement
        fetch (bool, optional): Whether to return query results
        
    Returns:
        list | None: Query results if fetch=True, otherwise None
        
    Raises:
        psycopg2.Error: Database operation errors
        
    Example:
        >>> db = Database()
        >>> # Insert operation
        >>> db.execute(
        ...     "INSERT INTO users (user_id, name) VALUES (%s, %s)",
        ...     (12345, "John Doe")
        ... )
        >>> 
        >>> # Select operation
        >>> users = db.execute(
        ...     "SELECT * FROM users WHERE user_id = %s",
        ...     (12345,),
        ...     fetch=True
        ... )
        >>> print(users[0]['name'])
        'John Doe'
    """
```

##### `create_tables()`
```python
def create_tables(self):
    """Initialize database tables if they don't exist.
    
    Creates the following tables:
    - users: User information
    - question_groups: Package definitions
    - questions: Question templates
    - user_groups: User-package associations
    - scheduled_questions: Question scheduling
    - user_answers: User responses
    
    Example:
        >>> db = Database()
        >>> db.create_tables()
        # Tables created successfully
    """
```

##### `init_question_data()`
```python
def init_question_data(self):
    """Initialize default question groups and questions.
    
    Inserts sample data for:
    - Question groups (1 month, 2 months, 3 months)
    - Sample questions for each group
    
    Example:
        >>> db = Database()
        >>> db.init_question_data()
        # Sample data inserted
    """
```

## Handlers Module

### Global Variables

```python
user_states: dict = {}
"""Global dictionary tracking user conversation states.

Structure:
{
    user_id: {
        "state": "current_state",
        "name": "user_name",
        "data": {...}
    }
}
"""
```

### Functions

##### `setup_handlers()`
```python
def setup_handlers(bot: TeleBot):
    """Setup all message handlers for the bot.
    
    Args:
        bot (TeleBot): Telegram bot instance
        
    Registers handlers for:
    - /start command
    - /help command  
    - All text messages
    
    Example:
        >>> from telebot import TeleBot
        >>> bot = TeleBot("your_token")
        >>> setup_handlers(bot)
        # Handlers registered successfully
    """
```

##### `start_handler()`
```python
@bot.message_handler(commands=['start'])
def start_handler(message):
    """Handle the /start command to begin interaction with user.
    
    Args:
        message: Telegram message object
        
    Flow:
        1. Extract user_id from message
        2. Send welcome message
        3. Set user state to "awaiting_name"
        
    Example:
        User sends: /start
        Bot replies: "Hello! Please enter your name:"
    """
```

##### `help_handler()`
```python
@bot.message_handler(commands=['help'])
def help_handler(message):
    """Handle the /help command to provide assistance.
    
    Args:
        message: Telegram message object
        
    Sends comprehensive help information including:
    - Available commands
    - Bot functionality
    - Usage instructions
    """
```

##### `handle_name()`
```python
def handle_name(bot: TeleBot, user_id: int, name: str):
    """Process user's name and save to database.
    
    Args:
        bot (TeleBot): Telegram bot instance
        user_id (int): Unique user identifier
        name (str): User's provided name
        
    Flow:
        1. Get username from Telegram
        2. Save user to database with UPSERT
        3. Update state to "awaiting_package"
        4. Send package selection keyboard
        
    Example:
        >>> handle_name(bot, 12345, "John Doe")
        # User saved, package options sent
    """
```

##### `handle_package()`
```python
def handle_package(bot: TeleBot, user_id: int, package: str):
    """Process user's package selection and schedule questions.
    
    Args:
        bot (TeleBot): Telegram bot instance
        user_id (int): Unique user identifier
        package (str): Selected package ("1 month", "2 months", "3 months")
        
    Flow:
        1. Validate package selection
        2. Create user-group association
        3. Schedule questions for selected package
        4. Send confirmation message
        5. Clear user state
        
    Raises:
        ValueError: If invalid package selected
        
    Example:
        >>> handle_package(bot, 12345, "1 month")
        # Package registered, questions scheduled
    """
```

##### `handle_answer()`
```python
def handle_answer(bot: TeleBot, user_id: int, answer: str):
    """Process user's answer to a question.
    
    Args:
        bot (TeleBot): Telegram bot instance
        user_id (int): Unique user identifier
        answer (str): User's answer to the question
        
    Flow:
        1. Find latest pending question
        2. Validate answer against question type
        3. Save answer to database
        4. Send confirmation
        
    Example:
        >>> handle_answer(bot, 12345, "Good")
        # Answer saved successfully
    """
```

## Scheduler Module

### Global Variables

```python
scheduler: BackgroundScheduler
"""APScheduler instance for background job management."""

logger: logging.Logger
"""Logger instance for scheduler events."""
```

### Functions

##### `setup_scheduler()`
```python
def setup_scheduler(bot: TeleBot):
    """Initialize and start scheduler jobs.
    
    Args:
        bot (TeleBot): Telegram bot instance for message sending
        
    Sets up two background jobs:
    - Question delivery (every QUESTION_CHECK_INTERVAL minutes)
    - Reminder sending (every REMINDER_CHECK_INTERVAL hours)
    
    Example:
        >>> from telebot import TeleBot
        >>> bot = TeleBot("token")
        >>> setup_scheduler(bot)
        # Scheduler started with 2 jobs
    """
```

##### `send_scheduled_questions()`
```python
def send_scheduled_questions(bot: TeleBot):
    """Send due questions to users.
    
    Args:
        bot (TeleBot): Telegram bot instance
        
    Process:
        1. Query for questions scheduled <= NOW() and not sent
        2. For each question:
           - Get question details
           - Create appropriate keyboard
           - Send to user
           - Mark as sent
           
    Error Handling:
        - Logs errors without stopping execution
        - Continues processing remaining questions
        
    Example:
        >>> send_scheduled_questions(bot)
        # Processed 5 questions, 3 sent successfully
    """
```

##### `send_reminders()`
```python
def send_reminders(bot: TeleBot):
    """Send reminders for unanswered questions.
    
    Args:
        bot (TeleBot): Telegram bot instance
        
    Process:
        1. Find questions sent > 24 hours ago without answers
        2. Send reminder messages with "REMINDER:" prefix
        3. Include original question keyboard
        
    Example:
        >>> send_reminders(bot)
        # Sent 2 reminders for overdue questions
    """
```

## Questions Module

### Functions

##### `get_question_text()`
```python
def get_question_text(question_id: int) -> str | None:
    """Get the text of a question by its ID.
    
    Args:
        question_id (int): Unique question identifier
        
    Returns:
        str | None: Question text or None if not found
        
    Example:
        >>> text = get_question_text(1)
        >>> print(text)
        "How are you feeling today?"
    """
```

##### `get_question_type()`
```python
def get_question_type(question_id: int) -> str | None:
    """Get the type of a question by its ID.
    
    Args:
        question_id (int): Unique question identifier
        
    Returns:
        str | None: Question type ('multiple_choice' or 'yes_no') or None
        
    Example:
        >>> qtype = get_question_type(1)
        >>> print(qtype)
        "multiple_choice"
    """
```

##### `get_question_options()`
```python
def get_question_options(question_id: int) -> list | None:
    """Get the options for a question by its ID.
    
    Args:
        question_id (int): Unique question identifier
        
    Returns:
        list | None: Question options or None if not applicable
        
    Example:
        >>> options = get_question_options(1)
        >>> print(options)
        ["Very good", "Good", "Satisfactory", "Bad"]
    """
```

##### `get_group_duration()`
```python
def get_group_duration(group_id: int) -> int | None:
    """Get the duration in days for a question group.
    
    Args:
        group_id (int): Question group identifier
        
    Returns:
        int | None: Duration in days or None if not found
        
    Example:
        >>> duration = get_group_duration(1)
        >>> print(duration)
        30
    """
```

##### `get_user_group_id()`
```python
def get_user_group_id(user_id: int) -> int | None:
    """Get the active group ID for a user.
    
    Args:
        user_id (int): Telegram user identifier
        
    Returns:
        int | None: User group ID or None if not found
        
    Example:
        >>> group_id = get_user_group_id(12345)
        >>> print(group_id)
        1
    """
```

## Utils Module

### Functions

##### `create_keyboard()`
```python
def create_keyboard(question_type: str, options: list = None) -> types.ReplyKeyboardMarkup:
    """Create a reply keyboard based on question type.
    
    Args:
        question_type (str): Type of question ('yes_no' or 'multiple_choice')
        options (list, optional): List of options for multiple choice
        
    Returns:
        ReplyKeyboardMarkup: Telegram keyboard markup
        
    Example:
        >>> # Yes/No keyboard
        >>> keyboard = create_keyboard('yes_no')
        >>> 
        >>> # Multiple choice keyboard
        >>> keyboard = create_keyboard('multiple_choice', ['Good', 'Bad', 'Neutral'])
    """
```

##### `get_package_options()`
```python
def get_package_options() -> types.ReplyKeyboardMarkup:
    """Create package selection keyboard.
    
    Returns:
        ReplyKeyboardMarkup: Keyboard with package options
        
    Packages:
        - 1 month
        - 2 months  
        - 3 months
        
    Example:
        >>> keyboard = get_package_options()
        >>> # Keyboard with 3 package options created
    """
```

##### `schedule_questions()`
```python
def schedule_questions(user_group_id: int, group_id: int):
    """Schedule all questions for a user group.
    
    Args:
        user_group_id (int): ID of the user-group association
        group_id (int): ID of the question group
        
    Process:
        1. Get questions for the group
        2. Get group duration and start date
        3. Calculate schedule using intervals and delays
        4. Insert scheduled questions into database
        
    Algorithm:
        For each question with interval I and delay D:
        - First occurrence: start_date + D days
        - Subsequent: previous + I days
        - Continue until: current_date > start_date + group_duration
        
    Example:
        >>> schedule_questions(1, 1)
        # Scheduled 15 questions over 30 days
    """
```

## Main Module

### Functions

##### `main()`
```python
def main():
    """Main function to initialize and run the bot.
    
    Process:
        1. Initialize database (create tables, insert sample data)
        2. Create TeleBot instance
        3. Setup message handlers
        4. Setup background scheduler
        5. Start bot polling in separate thread
        6. Keep main thread alive
        
    Error Handling:
        - Catches and logs initialization errors
        - Graceful shutdown on KeyboardInterrupt
        
    Example:
        >>> if __name__ == "__main__":
        ...     main()
        # Bot started successfully. Press Ctrl+C to stop.
    """
```

## Usage Examples

### Basic Bot Setup

```python
from telebot import TeleBot
from bot.config import config
from bot.database import db
from bot.handlers import setup_handlers
from bot.scheduler import setup_scheduler

# Initialize database
db.create_tables()
db.init_question_data()

# Create bot instance
bot = TeleBot(config.BOT_TOKEN)

# Setup components
setup_handlers(bot)
setup_scheduler(bot)

# Start bot
bot.infinity_polling()
```

### Database Operations

```python
from bot.database import db

# Insert user
db.execute(
    "INSERT INTO users (user_id, username, full_name) VALUES (%s, %s, %s)",
    (12345, "@johndoe", "John Doe")
)

# Query users
users = db.execute(
    "SELECT * FROM users WHERE user_id = %s",
    (12345,),
    fetch=True
)

# Update user
db.execute(
    "UPDATE users SET full_name = %s WHERE user_id = %s",
    ("John Smith", 12345)
)
```

### Question Management

```python
from bot.questions import get_question_text, get_question_type, get_question_options

# Get question details
question_id = 1
text = get_question_text(question_id)
qtype = get_question_type(question_id)
options = get_question_options(question_id)

print(f"Question: {text}")
print(f"Type: {qtype}")
print(f"Options: {options}")
```

### Custom Keyboard Creation

```python
from bot.utils import create_keyboard

# Create yes/no keyboard
yn_keyboard = create_keyboard('yes_no')

# Create multiple choice keyboard
mc_keyboard = create_keyboard(
    'multiple_choice', 
    ['Excellent', 'Good', 'Fair', 'Poor']
)

# Send message with keyboard
bot.send_message(
    user_id, 
    "How was your day?", 
    reply_markup=mc_keyboard
)
```

### Scheduler Job Management

```python
from bot.scheduler import scheduler, send_scheduled_questions

# Add custom job
scheduler.add_job(
    func=custom_function,
    trigger='cron',
    hour=9,
    minute=0,
    id='morning_reminder'
)

# Remove job
scheduler.remove_job('morning_reminder')

# Pause/Resume scheduler
scheduler.pause()
scheduler.resume()
```

## Error Codes

### Database Errors

| Code | Description | Solution |
|------|-------------|----------|
| `DB_001` | Connection failed | Check database configuration |
| `DB_002` | Query execution failed | Verify SQL syntax and parameters |
| `DB_003` | Transaction rollback | Check constraint violations |
| `DB_004` | Table not found | Run `create_tables()` |

### Bot API Errors

| Code | Description | Solution |
|------|-------------|----------|
| `BOT_001` | Invalid token | Verify BOT_TOKEN in environment |
| `BOT_002` | Rate limit exceeded | Implement rate limiting |
| `BOT_003` | User blocked bot | Handle ApiException gracefully |
| `BOT_004` | Message too long | Split message into chunks |

### Scheduler Errors

| Code | Description | Solution |
|------|-------------|----------|
| `SCH_001` | Job execution failed | Check job function for errors |
| `SCH_002` | Scheduler not running | Call `scheduler.start()` |
| `SCH_003` | Invalid cron expression | Verify trigger syntax |
| `SCH_004` | Job queue full | Increase max_workers |

### Application Errors

| Code | Description | Solution |
|------|-------------|----------|
| `APP_001` | Configuration missing | Set required environment variables |
| `APP_002` | Invalid user state | Reset user state in database |
| `APP_003` | Question not found | Verify question_id exists |
| `APP_004` | Package not available | Check available packages |

## Error Handling Patterns

### Database Error Handling

```python
try:
    result = db.execute("SELECT * FROM users", fetch=True)
except psycopg2.Error as e:
    logger.error(f"Database error: {e}")
    # Handle specific error types
    if e.pgcode == '23505':  # Unique violation
        return "User already exists"
    elif e.pgcode == '23502':  # Not null violation
        return "Required field missing"
    else:
        return "Database operation failed"
```

### Bot API Error Handling

```python
try:
    bot.send_message(user_id, message_text)
except telebot.apihelper.ApiException as e:
    if e.error_code == 403:
        logger.info(f"User {user_id} blocked the bot")
        # Mark user as inactive
    elif e.error_code == 429:
        logger.warning("Rate limit hit, retrying...")
        time.sleep(1)
        # Implement retry logic
    else:
        logger.error(f"API error {e.error_code}: {e.description}")
```

### Scheduler Error Handling

```python
def safe_job_execution(func):
    """Decorator for safe job execution"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Job {func.__name__} failed: {e}")
            # Optionally reschedule or alert administrators
    return wrapper

@safe_job_execution
def scheduled_task():
    # Task implementation
    pass
```

## Performance Considerations

### Database Optimization

```python
# Use indexes for frequently queried columns
db.execute("""
    CREATE INDEX IF NOT EXISTS idx_scheduled_questions_time 
    ON scheduled_questions(scheduled_time)
""")

# Batch operations
questions = [(user_id, question_id, schedule_time) for ...]
db.execute_many(
    "INSERT INTO scheduled_questions VALUES (%s, %s, %s)",
    questions
)
```

### Memory Management

```python
import gc

def cleanup_user_states():
    """Periodic cleanup of inactive user states"""
    current_time = time.time()
    inactive_users = []
    
    for user_id, state_data in user_states.items():
        if current_time - state_data.get('last_activity', 0) > 3600:
            inactive_users.append(user_id)
    
    for user_id in inactive_users:
        del user_states[user_id]
    
    gc.collect()  # Force garbage collection
```

### Rate Limiting

```python
from collections import defaultdict
import time

# Simple rate limiter
user_last_message = defaultdict(float)

def rate_limit_check(user_id, limit_seconds=1):
    """Check if user is rate limited"""
    now = time.time()
    if now - user_last_message[user_id] < limit_seconds:
        return False
    user_last_message[user_id] = now
    return True
```

---

## Author
**Saad Makki**  
Email: saadmakki116@gmail.com