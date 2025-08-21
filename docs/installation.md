# Installation Guide

This guide will walk you through setting up the Telegram Reminder Bot on different operating systems.

## 📋 Prerequisites

Before installing the bot, ensure you have:
- Python 3.8 or higher
- PostgreSQL database
- Telegram Bot Token (from @BotFather)
- Git (for cloning the repository)

## 🔧 Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-reminder-bot.git
cd telegram-reminder-bot
```

### Step 2: Platform-Specific Setup

#### 🐧 Linux (Ubuntu/Debian)

1. **Update system packages:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install Python and pip:**
```bash
sudo apt install python3 python3-pip python3-venv -y
```

3. **Install PostgreSQL:**
```bash
sudo apt install postgresql postgresql-contrib -y
```

4. **Setup PostgreSQL:**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE telegram_bot;
CREATE USER bot_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_bot TO bot_user;
\q
```

#### 🍎 macOS

1. **Install Homebrew (if not installed):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python:**
```bash
brew install python3
```

3. **Install PostgreSQL:**
```bash
brew install postgresql
brew services start postgresql
```

4. **Setup PostgreSQL:**
```bash
# Create database and user
createdb telegram_bot
psql telegram_bot

CREATE USER bot_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_bot TO bot_user;
\q
```

#### 🪟 Windows

1. **Install Python:**
   - Download Python from [python.org](https://python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Install PostgreSQL:**
   - Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - Follow the installation wizard
   - Remember the superuser password

3. **Setup PostgreSQL:**
   - Open pgAdmin or use Command Prompt:
```sql
-- In psql command line
CREATE DATABASE telegram_bot;
CREATE USER bot_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_bot TO bot_user;
```

### Step 3: Python Environment Setup

#### All Platforms

1. **Create virtual environment:**
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

1. **Create environment file:**
```bash
cp .env.example .env
```

2. **Edit the .env file:**
```bash
# Linux/macOS
nano .env

# Windows
notepad .env
```

3. **Add your configuration:**
```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Database Configuration
DB_NAME=telegram_bot
DB_USER=bot_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Scheduler Configuration
QUESTION_CHECK_INTERVAL=5
REMINDER_CHECK_INTERVAL=24
```

### Step 5: Database Initialization

```bash
python -c "from src.bot.database import db; db.create_tables(); db.init_question_data()"
```

### Step 6: Run the Bot

```bash
python src/main.py
```

## 🐳 Docker Installation (Optional)

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

1. **Create docker-compose.yml:**
```yaml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DB_HOST=postgres
      - DB_NAME=telegram_bot
      - DB_USER=bot_user
      - DB_PASSWORD=password123
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=telegram_bot
      - POSTGRES_USER=bot_user
      - POSTGRES_PASSWORD=password123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

2. **Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

3. **Run with Docker:**
```bash
docker-compose up -d
```

## 🔍 Verification

To verify the installation:

1. **Check bot status:**
   - Send `/start` to your bot on Telegram
   - You should receive a welcome message

2. **Check logs:**
```bash
# If running directly
python src/main.py

# If using Docker
docker-compose logs -f bot
```

3. **Check database:**
```sql
-- Connect to database
psql -h localhost -U bot_user -d telegram_bot

-- Check tables
\dt

-- Check sample data
SELECT * FROM question_groups;
SELECT * FROM questions LIMIT 5;
```

## 🚨 Troubleshooting

### Common Issues

#### Bot Token Issues
```bash
# Error: HTTP 401 Unauthorized
# Solution: Check your BOT_TOKEN in .env file
```

#### Database Connection Issues
```bash
# Error: could not connect to server
# Solution: Ensure PostgreSQL is running and credentials are correct

# Linux/macOS - Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Windows - Use Services manager or:
net start postgresql-x64-13
```

#### Permission Issues (Linux/macOS)
```bash
# If you get permission errors:
sudo chown -R $USER:$USER /path/to/project
chmod +x venv/bin/activate
```

#### Python Path Issues
```bash
# If modules are not found:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Windows:
set PYTHONPATH=%PYTHONPATH%;%CD%
```

### Port Issues
```bash
# If port 5432 is already in use:
# Change DB_PORT in .env to another port like 5433
# Or stop the conflicting service:

# Linux
sudo systemctl stop postgresql

# macOS
brew services stop postgresql

# Windows
net stop postgresql-x64-13
```

## 📊 Performance Optimization

### For Production Deployment

1. **Use connection pooling:**
```python
# Add to database.py
from psycopg2 import pool

connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **config.database_config)
```

2. **Configure logging:**
```python
# Add to main.py
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'bot.log', maxBytes=10*1024*1024, backupCount=5
)
```

3. **Set up monitoring:**
```bash
# Install monitoring tools
pip install psutil python-telegram-bot[socks]
```

## 🔄 Updates and Maintenance

### Updating the Bot

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations (if any)
python -c "from src.bot.database import db; db.create_tables()"

# Restart the bot
python src/main.py
```

### Backup Database

```bash
# Create backup
pg_dump -h localhost -U bot_user telegram_bot > backup_$(date +%Y%m%d).sql

# Restore backup
psql -h localhost -U bot_user telegram_bot < backup_20240101.sql
```

---

## 📞 Support

If you encounter any issues during installation, please:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [configuration guide](configuration.md)
3. Open an issue on GitHub
4. Contact the maintainer

---

**Author:** Saad Makki  
**Email:** saadmakki116@gmail.com