# Configuration Guide

This guide explains how to configure the Telegram Reminder Bot for different environments and use cases.

## 🔧 Environment Variables

All configuration is managed through environment variables. Create a `.env` file in the project root:

### Required Variables

```env
# Telegram Bot Token (Get from @BotFather)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz

# Database Configuration
DB_NAME=telegram_bot
DB_USER=bot_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Optional Variables

```env
# Scheduler Configuration (in minutes/hours)
QUESTION_CHECK_INTERVAL=5      # Check for due questions every 5 minutes
REMINDER_CHECK_INTERVAL=24     # Send reminders every 24 hours

# Logging Configuration
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=bot.log              # Log file path

# Database Connection Pool
DB_MIN_CONN=1                 # Minimum connections
DB_MAX_CONN=20                # Maximum connections
```

## 📋 Configuration Classes

### BotConfig Class

The `BotConfig` class in `src/bot/config.py` manages all configuration:

```python
class BotConfig:
    """Configuration class for bot settings."""
    
    # Telegram Bot Token (required)
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Database Configuration
    DB_NAME = os.getenv("DB_NAME", "telegram_bot")
    DB_USER = os.getenv("DB_USER", "bot_user") 
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
```

## 🌍 Environment-Specific Configurations

### Development Environment

```env
# .env.development
BOT_TOKEN=your_dev_bot_token
DB_NAME=telegram_bot_dev
DB_HOST=localhost
DB_PORT=5432
QUESTION_CHECK_INTERVAL=1
REMINDER_CHECK_INTERVAL=1
LOG_LEVEL=DEBUG
```

### Production Environment

```env
# .env.production
BOT_TOKEN=your_prod_bot_token
DB_NAME=telegram_bot_prod
DB_HOST=your_prod_db_host
DB_PORT=5432
QUESTION_CHECK_INTERVAL=5
REMINDER_CHECK_INTERVAL=24
LOG_LEVEL=INFO
```

### Testing Environment

```env
# .env.testing
BOT_TOKEN=your_test_bot_token
DB_NAME=telegram_bot_test
DB_HOST=localhost
DB_PORT=5432
QUESTION_CHECK_INTERVAL=1
REMINDER_CHECK_INTERVAL=1
LOG_LEVEL=DEBUG
```

## 🔐 Security Configuration

### Environment Variables Security

1. **Never commit `.env` files to version control**
```gitignore
# .gitignore
.env
.env.local
.env.production
.env.development
*.env
```

2. **Use strong passwords:**
```env
# Bad
DB_PASSWORD=123456

# Good
DB_PASSWORD=Xk9$mP2#vL8@nQ5*wR7^
```

3. **Restrict database access:**
```sql
-- Create user with limited permissions
CREATE USER bot_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE telegram_bot TO bot_user;
GRANT USAGE ON SCHEMA public TO bot_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bot_user;
```

### Bot Token Security

```python
# Validate bot token format
import re

def validate_bot_token(token):
    """Validate Telegram bot token format."""
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, token))

# Usage in config.py
if not validate_bot_token(BOT_TOKEN):
    raise ValueError("Invalid bot token format")
```

## 🗄️ Database Configuration

### Connection Parameters

```python
# Database connection configuration
DATABASE_CONFIG = {
    "dbname": "telegram_bot",
    "user": "bot_user", 
    "password": "secure_password",
    "host": "localhost",
    "port": "5432",
    "sslmode": "prefer",           # SSL connection mode
    "connect_timeout": 10,         # Connection timeout
    "application_name": "TelegramBot"  # Application identifier
}
```

### Connection Pooling

```python
# Advanced database configuration with connection pooling
from psycopg2 import pool

class DatabaseConfig:
    def __init__(self):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            **config.database_config
        )
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def put_connection(self, conn):
        self.connection_pool.putconn(conn)
```

### Database URL Format

For some deployments, you might need a DATABASE_URL:

```env
# Format: postgresql://user:password@host:port/database
DATABASE_URL=postgresql://bot_user:password@localhost:5432/telegram_bot
```

```python
# Parse DATABASE_URL
import os
from urllib.parse import urlparse

def parse_database_url(url):
    """Parse database URL into components."""
    parsed = urlparse(url)
    return {
        "dbname": parsed.path[1:],
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port or 5432
    }

# Usage
if os.getenv("DATABASE_URL"):
    DB_CONFIG = parse_database_url(os.getenv("DATABASE_URL"))
```

## ⏰ Scheduler Configuration

### Timing Settings

```python
class SchedulerConfig:
    """Scheduler configuration settings."""
    
    # Check for due questions every N minutes
    QUESTION_CHECK_INTERVAL = 5
    
    # Send reminders every N hours  
    REMINDER_CHECK_INTERVAL = 24
    
    # Timezone for scheduling
    TIMEZONE = 'UTC'
    
    # Maximum retries for failed jobs
    MAX_RETRIES = 3
    
    # Job coalescing (combine similar jobs)
    COALESCE = True
```

### Advanced Scheduler Setup

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

def create_scheduler():
    """Create configured scheduler."""
    
    # Job stores
    jobstores = {
        'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    }
    
    # Executors
    executors = {
        'default': ThreadPoolExecutor(20),
    }
    
    # Job defaults
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    
    return BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC'
    )
```

## 📊 Logging Configuration

### Basic Logging Setup

```python
import logging
import logging.handlers

def setup_logging():
    """Configure logging for the bot."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
```

### Environment-Specific Logging

```python
def get_log_level():
    """Get log level from environment."""
    level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    return getattr(logging, level_name, logging.INFO)

def setup_logging():
    logging.basicConfig(
        level=get_log_level(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.getenv('LOG_FILE', 'bot.log')),
            logging.StreamHandler()
        ]
    )
```

## 🔄 Configuration Validation

### Validation Methods

```python
class ConfigValidator:
    """Validate configuration settings."""
    
    def validate_required_vars(self):
        """Validate all required variables are present."""
        required = ['BOT_TOKEN', 'DB_PASSWORD']
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
    
    def validate_database_connection(self):
        """Test database connection."""
        try:
            conn = psycopg2.connect(**config.database_config)
            conn.close()
            return True
        except Exception as e:
            raise ConnectionError(f"Database connection failed: {e}")
    
    def validate_bot_token(self):
        """Test bot token validity."""
        import requests
        
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe"
        response = requests.get(url)
        
        if not response.json().get('ok'):
            raise ValueError("Invalid bot token")
```

### Configuration Loading

```python
def load_configuration():
    """Load and validate configuration."""
    
    # Load environment variables
    load_dotenv()
    
    # Create config instance
    config = BotConfig()
    
    # Validate configuration
    validator = ConfigValidator()
    validator.validate_required_vars()
    validator.validate_database_connection()
    validator.validate_bot_token()
    
    return config
```

## 🚀 Deployment Configurations

### Heroku Configuration

```bash
# Set Heroku environment variables
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set DB_HOST=your_heroku_postgres_host
heroku config:set DB_NAME=your_heroku_db_name
heroku config:set DB_USER=your_heroku_db_user
heroku config:set DB_PASSWORD=your_heroku_db_password
heroku config:set DB_PORT=5432
```

### Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DB_HOST=postgres
      - DB_NAME=telegram_bot
      - DB_USER=bot_user
      - DB_PASSWORD=${DB_PASSWORD}
      - QUESTION_CHECK_INTERVAL=5
      - REMINDER_CHECK_INTERVAL=24
    env_file:
      - .env
```

### Railway Configuration

```bash
# railway environment variables
railway variables set BOT_TOKEN=your_bot_token
railway variables set DATABASE_URL=your_postgres_url
```

## 🔧 Custom Configuration

### Adding New Configuration Options

1. **Add to environment variables:**
```env
# New feature toggle
ENABLE_ANALYTICS=true
ANALYTICS_API_KEY=your_analytics_key
```

2. **Add to BotConfig class:**
```python
class BotConfig:
    # Existing config...
    
    # Analytics configuration
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "false").lower() == "true"
    ANALYTICS_API_KEY = os.getenv("ANALYTICS_API_KEY")
```

3. **Use in your code:**
```python
from src.bot.config import config

if config.ENABLE_ANALYTICS:
    # Initialize analytics
    analytics.initialize(config.ANALYTICS_API_KEY)
```

## 📋 Configuration Checklist

### Pre-deployment Checklist

- [ ] All required environment variables set
- [ ] Database credentials are correct
- [ ] Bot token is valid
- [ ] Scheduler intervals are appropriate
- [ ] Logging is configured
- [ ] Security settings are in place
- [ ] Backup strategy is defined

### Production Checklist

- [ ] `.env` file is not in version control
- [ ] Strong passwords are used
- [ ] Database connections are secured
- [ ] Monitoring is enabled
- [ ] Error handling is implemented
- [ ] Performance metrics are tracked

---

**Author:** Saad Makki  
**Email:** saadmakki116@gmail.com