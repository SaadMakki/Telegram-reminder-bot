import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.bot.scheduler import send_scheduled_questions, send_reminders

class TestScheduler(unittest.TestCase):
    """Test cases for the scheduler functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bot = MagicMock()
        self.mock_db = MagicMock()
    
    @patch('src.bot.scheduler.db')
    @patch('src.bot.scheduler.get_question_text')
    @patch('src.bot.scheduler.get_question_type')
    @patch('src.bot.scheduler.get_question_options')
    @patch('src.bot.scheduler.create_keyboard')
    def test_send_scheduled_questions(self, mock_create_keyboard, mock_get_options, 
                                    mock_get_type, mock_get_text, mock_db):
        """Test sending scheduled questions."""
        # Mock database response
        mock_db.execute.return_value = [
            {'schedule_id': 1, 'user_id': 12345, 'question_id': 1},
            {'schedule_id': 2, 'user_id': 67890, 'question_id': 2}
        ]
        
        # Mock question details
        mock_get_text.return_value = "How are you feeling today?"
        mock_get_type.return_value = "multiple_choice"
        mock_get_options.return_value = ["Good", "Bad"]
        mock_create_keyboard.return_value = MagicMock()
        
        send_scheduled_questions(self.bot)
        
        # Check that questions were sent
        self.assertEqual(self.bot.send_message.call_count, 2)
        # Check that schedule status was updated
        self.assertEqual(mock_db.execute.call_count, 3)  # 1 for query, 2 for updates
    
    @patch('src.bot.scheduler.db')
    @patch('src.bot.scheduler.get_question_text')
    @patch('src.bot.scheduler.get_question_type')
    @patch('src.bot.scheduler.get_question_options')
    @patch('src.bot.scheduler.create_keyboard')
    def test_send_scheduled_questions_no_due(self, mock_create_keyboard, mock_get_options, 
                                           mock_get_type, mock_get_text, mock_db):
        """Test sending scheduled questions when none are due."""
        # Mock empty database response
        mock_db.execute.return_value = []
        
        send_scheduled_questions(self.bot)
        
        # Check that no messages were sent
        self.bot.send_message.assert_not_called()
    
    @patch('src.bot.scheduler.db')
    @patch('src.bot.scheduler.get_question_text')
    @patch('src.bot.scheduler.get_question_type')
    @patch('src.bot.scheduler.get_question_options')
    @patch('src.bot.scheduler.create_keyboard')
    def test_send_reminders(self, mock_create_keyboard, mock_get_options, 
                          mock_get_type, mock_get_text, mock_db):
        """Test sending reminders for unanswered questions."""
        # Mock database response
        mock_db.execute.return_value = [
            {'schedule_id': 1, 'user_id': 12345, 'question_id': 1},
            {'schedule_id': 2, 'user_id': 67890, 'question_id': 2}
        ]
        
        # Mock question details
        mock_get_text.return_value = "How are you feeling today?"
        mock_get_type.return_value = "multiple_choice"
        mock_get_options.return_value = ["Good", "Bad"]
        mock_create_keyboard.return_value = MagicMock()
        
        send_reminders(self.bot)
        
        # Check that reminders were sent
        self.assertEqual(self.bot.send_message.call_count, 2)
    
    @patch('src.bot.scheduler.db')
    def test_send_reminders_none(self, mock_db):
        """Test sending reminders when there are none to send."""
        # Mock empty database response
        mock_db.execute.return_value = []
        
        send_reminders(self.bot)
        
        # Check that no messages were sent
        self.bot.send_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()