import psycopg2
import psycopg2.extras
import config

class Database:
    def __init__(self):
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**config.DB_CONFIG())
        return self.conn
    
    def execute(self, query, params=None, fetch=False):
        """Execute SQL query with optional parameters"""
        conn = self.connect()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def create_tables(self):
        """Initialize database tables"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                full_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS question_groups (
                group_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                duration_days INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS questions (
                question_id SERIAL PRIMARY KEY,
                group_id INTEGER REFERENCES question_groups(group_id),
                text TEXT NOT NULL,
                type VARCHAR(20) CHECK (type IN ('multiple_choice', 'yes_no')),
                options JSONB,
                interval_days INTEGER NOT NULL,
                delay_days INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_groups (
                user_group_id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                group_id INTEGER REFERENCES question_groups(group_id),
                start_date TIMESTAMP NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS scheduled_questions (
                schedule_id SERIAL PRIMARY KEY,
                user_group_id INTEGER REFERENCES user_groups(user_group_id),
                question_id INTEGER REFERENCES questions(question_id),
                scheduled_time TIMESTAMP NOT NULL,
                sent BOOLEAN DEFAULT FALSE,
                sent_time TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_answers (
                answer_id SERIAL PRIMARY KEY,
                schedule_id INTEGER REFERENCES scheduled_questions(schedule_id),
                answer TEXT NOT NULL,
                answered_at TIMESTAMP DEFAULT NOW()
            )
            """
        ]
        
        for query in queries:
            self.execute(query)
    
    def init_question_data(self):
        """Initialize default question groups and questions"""
        # Insert question groups
        groups = [
            ("1 айлык", 30),
            ("2 айлык", 60),
            ("3 айлык", 90)
        ]
        
        for name, duration in groups:
            self.execute(
                "INSERT INTO question_groups (name, duration_days) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (name, duration)
            )
        
        # Insert sample questions
        questions = [
            (1, "Сіз бүгін өзіңізді қалай сезінесіз?", "multiple_choice", 
             ["Өте жақсы", "Жақсы", "Қанағаттанарлық", "Нашар"], 1, 0),
            (1, "Дәрілерді үзбей қабылдадыңыз ба?", "yes_no", None, 10, 10),
            (2, "Сіздің жалпы денсаулығыңыз қалай?", "multiple_choice", 
             ["Өте жақсы", "Жақсы", "Қанағаттанарлық", "Нашар"], 5, 5),
            (3, "Сіздің энергия деңгейіңіз қалай?", "multiple_choice", 
             ["Жоғары", "Орташа", "Төмен"], 3, 2)
        ]
        
        for group_id, text, qtype, options, interval, delay in questions:
            self.execute(
                """INSERT INTO questions (group_id, text, type, options, interval_days, delay_days)
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (group_id, text, qtype, options, interval, delay)
            )

# Singleton database instance
db = Database()