import psycopg2
import psycopg2.extras
from .config import config

class Database:
    """Database class to handle PostgreSQL connections and operations."""
    
    def __init__(self):
        """Initialize database connection."""
        self.conn = None
        
    def connect(self):
        """Establish database connection if not already connected."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**config.DB_CONFIG)
        return self.conn
    
    def execute(self, query, params=None, fetch=False):
        """
        Execute SQL query with optional parameters.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters
            fetch (bool): Whether to fetch results
            
        Returns:
            list: Query results if fetch=True, otherwise None
        """
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
        """Initialize database tables if they don't exist."""
        queries = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                full_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # Question groups table
            """
            CREATE TABLE IF NOT EXISTS question_groups (
                group_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                duration_days INTEGER NOT NULL
            )
            """,
            # Questions table
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
            # User groups table
            """
            CREATE TABLE IF NOT EXISTS user_groups (
                user_group_id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                group_id INTEGER REFERENCES question_groups(group_id),
                start_date TIMESTAMP NOT NULL
            )
            """,
            # Scheduled questions table
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
            # User answers table
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
        """Initialize default question groups and questions."""
        # Insert question groups
        groups = [
            ("1 month", 30),
            ("2 months", 60),
            ("3 months", 90)
        ]
        
        for name, duration in groups:
            self.execute(
                "INSERT INTO question_groups (name, duration_days) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (name, duration)
            )
        
        # Insert sample questions
        questions = [
            (1, "How are you feeling today?", "multiple_choice", 
             ["Very good", "Good", "Satisfactory", "Bad"], 1, 0),
            (1, "Did you take your medication regularly?", "yes_no", None, 10, 10),
            (2, "How is your overall health?", "multiple_choice", 
             ["Very good", "Good", "Satisfactory", "Bad"], 5, 5),
            (3, "How is your energy level?", "multiple_choice", 
             ["High", "Medium", "Low"], 3, 2)
        ]
        
        for group_id, text, qtype, options, interval, delay in questions:
            self.execute(
                """INSERT INTO questions (group_id, text, type, options, interval_days, delay_days)
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (group_id, text, qtype, options, interval, delay)
            )

# Create a global database instance
db = Database()