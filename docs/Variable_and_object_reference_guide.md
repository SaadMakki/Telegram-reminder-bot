# Variable and Object Reference Guide

This comprehensive guide documents every variable, object, and data structure used in the Telegram Reminder Bot, along with their types, purposes, and theoretical foundations.

## Table of Contents
- [Configuration Variables](#configuration-variables)
- [Database Objects](#database-objects)
- [Bot Handler Objects](#bot-handler-objects)
- [Scheduler Objects](#scheduler-objects)
- [Utility Objects](#utility-objects)
- [Programming Theories Applied](#programming-theories-applied)
- [Data Structures and Algorithms](#data-structures-and-algorithms)

## Configuration Variables

| Variable | Type | Purpose | Location | Theory Applied |
|----------|------|---------|----------|----------------|
| `BOT_TOKEN` | `str` | Telegram Bot API authentication token | `config.py` | **Secure Authentication Pattern** |
| `DB_NAME` | `str` | PostgreSQL database name | `config.py` | **Configuration Management Pattern** |
| `DB_USER` | `str` | Database username for authentication | `config.py` | **Separation of Concerns** |
| `DB_PASSWORD` | `str` | Database password (sensitive data) | `config.py` | **Security by Design** |
| `DB_HOST` | `str` | Database server hostname/IP | `config.py` | **Network Abstraction** |
| `DB_PORT` | `str` | Database server port number | `config.py` | **Port Abstraction** |
| `QUESTION_CHECK_INTERVAL` | `int` | Scheduler interval for question checks (minutes) | `config.py` | **Polling Pattern** |
| `REMINDER_CHECK_INTERVAL` | `int` | Scheduler interval for reminder checks (hours) | `config.py` | **Batch Processing** |

### Example Implementation:
```python
class Config:
    """Configuration class implementing Singleton Pattern for centralized config management"""
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # Environment variable injection
    DB_NAME = os.getenv("DB_NAME", "telegram_bot")  # Default value fallback
    
    @property
    def DB_CONFIG(self):
        """Factory method returning database configuration dictionary"""
        return {
            "dbname": self.DB_NAME,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "host": self.DB_HOST,
            "port": self.DB_PORT
        }
```

**Resources:**
- [Configuration Management Patterns](https://martinfowler.com/articles/injection.html)
- [Environment Variable Best Practices](https://12factor.net/config)

## Database Objects

| Object/Variable | Type | Purpose | Location | Theory Applied |
|-----------------|------|---------|----------|----------------|
| `conn` | `psycopg2.connection` | PostgreSQL database connection object | `database.py` | **Connection Pool Pattern** |
| `cursor` | `psycopg2.cursor` | Database cursor for executing SQL commands | `database.py` | **Command Pattern** |
| `db` | `Database` | Global database instance (Singleton) | `database.py` | **Singleton Pattern** |
| `user_id` | `BIGINT` | Unique Telegram user identifier | Database Schema | **Primary Key Constraint** |
| `question_id` | `SERIAL` | Auto-incrementing question identifier | Database Schema | **Auto-increment Pattern** |
| `group_id` | `SERIAL` | Auto-incrementing group identifier | Database Schema | **Foreign Key Relationship** |
| `schedule_id` | `SERIAL` | Unique identifier for scheduled questions | Database Schema | **Composite Key Design** |

### Database Class Implementation:
```python
class Database:
    """Database abstraction layer implementing Repository Pattern"""
    
    def __init__(self):
        """Constructor implementing lazy initialization"""
        self.conn = None
        
    def connect(self):
        """Connection factory with connection reuse pattern"""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**config.DB_CONFIG)
        return self.conn
    
    def execute(self, query, params=None, fetch=False):
        """Generic query executor implementing Command Pattern"""
        conn = self.connect()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params)  # Parameterized queries prevent SQL injection
                if fetch:
                    return cur.fetchall()
                conn.commit()  # Transaction management
        except Exception as e:
            conn.rollback()  # ACID compliance
            raise e
```

**Resources:**
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Database Connection Patterns](https://www.postgresql.org/docs/current/libpq-connect.html)

## Bot Handler Objects

| Variable | Type | Purpose | Location | Theory Applied |
|----------|------|---------|----------|----------------|
| `bot` | `TeleBot` | Main Telegram Bot API wrapper instance | `handlers.py` | **Facade Pattern** |
| `user_states` | `dict` | In-memory user conversation state tracking | `handlers.py` | **State Machine Pattern** |
| `message` | `types.Message` | Telegram message object containing user input | `handlers.py` | **Data Transfer Object** |
| `user_id` | `int` | Extracted user identifier from message | `handlers.py` | **Data Extraction Pattern** |
| `text` | `str` | User's message text content | `handlers.py` | **Input Validation** |
| `markup` | `types.ReplyKeyboardMarkup` | Telegram inline keyboard for user responses | `handlers.py` | **Command Pattern** |

### State Management Implementation:
```python
# Global state dictionary implementing State Machine Pattern
user_states = {}  # {user_id: {"state": "current_state", "data": {...}}}

def handle_name(bot, user_id, name):
    """State transition handler implementing Finite State Machine"""
    # State validation
    if user_id not in user_states:
        return
    
    # Database transaction (ACID properties)
    db.execute(
        """INSERT INTO users (user_id, username, full_name, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
        full_name = EXCLUDED.full_name, username = EXCLUDED.username""",
        (user_id, username, name, datetime.datetime.now())
    )
    
    # State transition
    user_states[user_id] = {"state": "awaiting_package", "name": name}
```

**Resources:**
- [State Machine Pattern](https://refactoring.guru/design-patterns/state)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)

## Scheduler Objects

| Variable | Type | Purpose | Location | Theory Applied |
|----------|------|---------|----------|----------------|
| `scheduler` | `BackgroundScheduler` | APScheduler instance for background job execution | `scheduler.py` | **Observer Pattern** |
| `logger` | `logging.Logger` | Logging instance for scheduler events | `scheduler.py` | **Logging Pattern** |
| `schedule_id` | `int` | Database identifier for scheduled question | `scheduler.py` | **Unique Identifier Pattern** |
| `scheduled_time` | `datetime` | Timestamp when question should be sent | `scheduler.py` | **Temporal Data Pattern** |
| `sent` | `bool` | Boolean flag indicating if question was sent | `scheduler.py` | **Flag Pattern** |

### Scheduler Implementation:
```python
from apscheduler.schedulers.background import BackgroundScheduler

# Global scheduler instance (Singleton Pattern)
scheduler = BackgroundScheduler()

def setup_scheduler(bot: TeleBot):
    """Factory method for scheduler configuration"""
    # Cron-like job scheduling using Observer Pattern
    scheduler.add_job(
        lambda: send_scheduled_questions(bot),  # Lambda for closure
        'interval',
        minutes=config.QUESTION_CHECK_INTERVAL
    )
    
    scheduler.start()  # Background thread management

def send_scheduled_questions(bot: TeleBot):
    """Batch processing implementation for question delivery"""
    try:
        # SQL query with JOIN operations (Relational Algebra)
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
        
        # Batch processing with error handling
        for row in results:
            # Process each scheduled question
            send_question_to_user(bot, row)
            
    except Exception as e:
        logger.error("Error sending questions: %s", e)  # Error logging
```

**Resources:**
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Observer Pattern](https://refactoring.guru/design-patterns/observer)

## Utility Objects

| Variable | Type | Purpose | Location | Theory Applied |
|----------|------|---------|----------|----------------|
| `markup` | `ReplyKeyboardMarkup` | Telegram keyboard UI component | `utils.py` | **Builder Pattern** |
| `current_date` | `datetime` | Iterator for date calculations | `utils.py` | **Iterator Pattern** |
| `end_date` | `datetime` | Boundary condition for scheduling | `utils.py` | **Boundary Value Analysis** |
| `interval` | `int` | Days between question repetitions | `utils.py` | **Interval Scheduling Algorithm** |
| `delay` | `int` | Initial delay before first question | `utils.py` | **Delayed Execution Pattern** |

### Utility Functions Implementation:
```python
def create_keyboard(question_type, options=None):
    """Factory method implementing Builder Pattern for UI components"""
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=True,  # Single-use keyboard
        resize_keyboard=True     # Responsive design
    )
    
    if question_type == 'yes_no':
        markup.add("Yes", "No")  # Binary choice pattern
    elif question_type == 'multiple_choice' and options:
        for option in options:  # Iterator pattern
            markup.add(option)
    
    return markup

def schedule_questions(user_group_id, group_id):
    """Interval scheduling algorithm implementation"""
    # Get questions using Repository Pattern
    questions = db.execute(
        "SELECT question_id, interval_days, delay_days FROM questions WHERE group_id = %s",
        (group_id,),
        fetch=True
    )
    
    # Calculate scheduling using arithmetic progression
    for question in questions:
        question_id = question['question_id']
        interval = question['interval_days']  # Common difference
        delay = question['delay_days']        # Initial term
        
        # Arithmetic sequence: a_n = a_1 + (n-1)d
        current_date = start_date + timedelta(days=delay)
        
        # Generate schedule until boundary condition
        while current_date <= end_date:
            # Insert scheduled question
            db.execute(
                "INSERT INTO scheduled_questions (user_group_id, question_id, scheduled_time) VALUES (%s, %s, %s)",
                (user_group_id, question_id, current_date)
            )
            current_date += timedelta(days=interval)  # Increment by common difference
```

**Resources:**
- [Builder Pattern](https://refactoring.guru/design-patterns/builder)
- [Interval Scheduling Algorithms](https://en.wikipedia.org/wiki/Interval_scheduling)

## Programming Theories Applied

### 1. Object-Oriented Programming (OOP)

The codebase extensively uses OOP principles:

#### Encapsulation
```python
class Config:
    """Encapsulation of configuration data and methods"""
    def __init__(self):
        self._bot_token = os.getenv("BOT_TOKEN")  # Private attribute
    
    @property
    def BOT_TOKEN(self):
        """Controlled access to sensitive data"""
        return self._bot_token
```

#### Inheritance
```python
class Database:
    """Base database operations"""
    def execute(self, query, params=None, fetch=False):
        # Base implementation
        pass

class ExtendedDatabase(Database):
    """Extended database with additional features"""
    def execute_batch(self, queries):
        # Extended functionality
        pass
```

### 2. SOLID Principles

#### Single Responsibility Principle (SRP)
Each class has a single responsibility:
- `Config`: Configuration management only
- `Database`: Database operations only
- `TeleBot`: Telegram API interactions only

#### Open/Closed Principle (OCP)
```python
def setup_handlers(bot: TeleBot):
    """Open for extension, closed for modification"""
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        # Handler implementation
        pass
    
    # New handlers can be added without modifying existing ones
```

### 3. Design Patterns

#### Singleton Pattern
```python
# Global instances ensure single point of access
config = Config()  # Single configuration instance
db = Database()    # Single database connection manager
```

#### Factory Pattern
```python
def create_keyboard(question_type, options=None):
    """Factory method creating different keyboard types"""
    if question_type == 'yes_no':
        return create_yes_no_keyboard()
    elif question_type == 'multiple_choice':
        return create_multiple_choice_keyboard(options)
```

#### Observer Pattern
```python
# Scheduler observes time intervals and notifies bot
scheduler.add_job(
    lambda: send_scheduled_questions(bot),  # Observer callback
    'interval',
    minutes=config.QUESTION_CHECK_INTERVAL
)
```

### 4. Database Theory

#### ACID Properties
```python
def execute(self, query, params=None, fetch=False):
    """Ensures ACID compliance in database operations"""
    conn = self.connect()
    try:
        with conn.cursor() as cur:  # Atomicity
            cur.execute(query, params)  # Consistency through constraints
            if fetch:
                return cur.fetchall()
            conn.commit()  # Durability
    except Exception as e:
        conn.rollback()  # Isolation through rollback
        raise e
```

#### Relational Algebra
```sql
-- JOIN operations implementing relational algebra
SELECT sq.schedule_id, u.user_id, q.question_id
FROM scheduled_questions sq  -- Relation R1
JOIN user_groups ug ON sq.user_group_id = ug.user_group_id  -- R1 ⋈ R2
JOIN users u ON ug.user_id = u.user_id  -- (R1 ⋈ R2) ⋈ R3
JOIN questions q ON sq.question_id = q.question_id  -- ((R1 ⋈ R2) ⋈ R3) ⋈ R4
WHERE sq.sent = FALSE  -- Selection σ
```

### 5. Concurrency Theory

#### Thread Safety
```python
import threading

# Thread-safe scheduler for background jobs
scheduler = BackgroundScheduler()

def polling_thread():
    """Separate thread for bot polling"""
    bot.infinity_polling()

polling_thread = threading.Thread(target=polling_thread, daemon=True)
```

#### Race Condition Prevention
```python
# Database transactions prevent race conditions
with conn.cursor() as cur:
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    # Atomic operation prevents concurrent modification
    cur.execute("UPDATE users SET last_seen = NOW() WHERE user_id = %s", (user_id,))
    conn.commit()
```

## Data Structures and Algorithms

### 1. Hash Tables (Dictionaries)
```python
# O(1) average-case lookup for user states
user_states = {
    12345: {"state": "awaiting_name", "data": {...}},
    67890: {"state": "awaiting_package", "data": {...}}
}

# Fast state retrieval
current_state = user_states.get(user_id, {}).get("state")
```

### 2. Queue Data Structure
```python
# APScheduler uses priority queues for job scheduling
# Jobs are queued and executed based on scheduled time
scheduler.add_job(
    func=send_scheduled_questions,
    trigger='interval',
    minutes=5  # Priority based on execution time
)
```

### 3. Tree Traversal (SQL Query Planning)
```sql
-- Database query planner uses tree structures
-- for JOIN optimization and execution planning
EXPLAIN (FORMAT JSON)
SELECT *
FROM scheduled_questions sq
JOIN user_groups ug ON sq.user_group_id = ug.user_group_id;
```

### 4. Interval Scheduling Algorithm
```python
def schedule_questions(user_group_id, group_id):
    """Greedy algorithm for optimal interval scheduling"""
    for question in questions:
        current_date = start_date + timedelta(days=question['delay_days'])
        
        # Greedy choice: schedule at earliest possible time
        while current_date <= end_date:
            schedule_question(current_date)
            current_date += timedelta(days=question['interval_days'])
```

### Time Complexity Analysis

| Operation | Time Complexity | Space Complexity | Data Structure |
|-----------|----------------|------------------|----------------|
| User State Lookup | O(1) average | O(n) | Hash Table |
| Database Query | O(log n) | O(1) | B-Tree Index |
| Question Scheduling | O(n) | O(n) | Array/List |
| Message Processing | O(1) | O(1) | Queue |

## Architectural Patterns

### 1. Model-View-Controller (MVC)
- **Model**: Database classes (`database.py`, `questions.py`)
- **View**: Telegram UI (keyboards, messages)
- **Controller**: Handler functions (`handlers.py`)

### 2. Repository Pattern
```python
class Database:
    """Repository providing abstract interface to data layer"""
    def find_user(self, user_id):
        return self.execute("SELECT * FROM users WHERE user_id = %s", (user_id,), fetch=True)
    
    def save_user(self, user_data):
        return self.execute("INSERT INTO users (...) VALUES (...)", user_data)
```

### 3. Dependency Injection
```python
def setup_handlers(bot: TeleBot):
    """Dependency injection of bot instance into handlers"""
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        # Bot dependency injected through closure
        bot.send_message(message.chat.id, "Hello!")
```

**Resources:**
- [Design Patterns: Elements of Reusable Object-Oriented Software](https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612)
- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Database Systems: The Complete Book](https://www.amazon.com/Database-Systems-Complete-Book-2nd/dp/0131873253)
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

---

## Author
**Saad Makki**  
Email: saadmakki116@gmail.com