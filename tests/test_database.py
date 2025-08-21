import unittest
from unittest.mock import patch, MagicMock
import psycopg2
from src.bot.database import Database

class TestDatabase(unittest.TestCase):
    """Test cases for the Database class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = Database()
        # Mock the connection
        self.db.conn = MagicMock()
    
    def test_connect_creates_new_connection(self):
        """Test that connect creates a new connection when none exists."""
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            self.db.conn = None
            
            result = self.db.connect()
            
            mock_connect.assert_called_once()
            self.assertEqual(result, mock_conn)
            self.assertEqual(self.db.conn, mock_conn)
    
    def test_connect_reuses_existing_connection(self):
        """Test that connect reuses existing connection."""
        mock_conn = MagicMock()
        self.db.conn = mock_conn
        
        result = self.db.connect()
        
        self.assertEqual(result, mock_conn)
    
    def test_execute_success(self):
        """Test successful execution of a query."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        self.db.conn = mock_conn
        
        query = "SELECT * FROM users"
        params = (1,)
        
        self.db.execute(query, params)
        
        mock_cursor.execute.assert_called_once_with(query, params)
        mock_conn.commit.assert_called_once()
    
    def test_execute_with_fetch(self):
        """Test execution of a query with fetch."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{'user_id': 1}]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        self.db.conn = mock_conn
        
        query = "SELECT * FROM users WHERE user_id = %s"
        params = (1,)
        
        result = self.db.execute(query, params, fetch=True)
        
        mock_cursor.execute.assert_called_once_with(query, params)
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, [{'user_id': 1}])
    
    def test_execute_with_error(self):
        """Test execution of a query that raises an error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Test error")
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        self.db.conn = mock_conn
        
        query = "SELECT * FROM users"
        
        with self.assertRaises(Exception):
            self.db.execute(query)
        
        mock_conn.rollback.assert_called_once()

if __name__ == '__main__':
    unittest.main()