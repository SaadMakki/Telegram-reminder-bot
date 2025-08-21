import unittest
from unittest.mock import patch, MagicMock
from telebot import types
from src.bot.handlers import setup_handlers, handle_name, handle_package, handle_answer

class TestHandlers(unittest.TestCase):
    """Test cases for the bot handlers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bot = MagicMock()
        self.user_id = 12345
        self.chat = types.Chat(self.user_id, 'private')
        self.message = types.Message(1, None, self.chat, 'text', {}, '')
    
    @patch('src.bot.handlers.user_states', {})
    def test_start_handler(self):
        """Test the start command handler."""
        self.message.text = '/start'
        
        setup_handlers(self.bot)
        # Find the start handler and call it
        for handler in self.bot.message_handler.call_args_list:
            if handler[1].get('commands') == ['start']:
                handler_func = handler[0][0]
                handler_func(self.message)
                break
        
        self.bot.send_message.assert_called_with(
            self.user_id, 
            "Hello! Please enter your name:"
        )
        self.assertEqual(self.bot.handlers.user_states.get(self.user_id, {}).get('state'), 'awaiting_name')
    
    @patch('src.bot.handlers.db')
    @patch('src.bot.handlers.user_states', {12345: {'state': 'awaiting_name'}})
    def test_handle_name(self):
        """Test the name handler."""
        name = "Test User"
        
        # Mock the bot's get_chat method
        mock_chat = MagicMock()
        mock_chat.username = 'testuser'
        self.bot.get_chat.return_value = mock_chat
        
        handle_name(self.bot, self.user_id, name)
        
        # Check that the user was saved to the database
        self.bot.handlers.db.execute.assert_called()
        # Check that the next message was sent
        self.bot.send_message.assert_called_with(
            self.user_id, 
            "Please select a package:", 
            reply_markup=self.bot.handlers.get_package_options()
        )
        # Check that the state was updated
        self.assertEqual(self.bot.handlers.user_states[self.user_id]['state'], 'awaiting_package')
        self.assertEqual(self.bot.handlers.user_states[self.user_id]['name'], name)
    
    @patch('src.bot.handlers.db')
    @patch('src.bot.handlers.schedule_questions')
    @patch('src.bot.handlers.user_states', {12345: {'state': 'awaiting_package', 'name': 'Test User'}})
    def test_handle_package_valid(self):
        """Test the package handler with a valid package."""
        package = "1 month"
        
        # Mock database response
        mock_db_result = [{'user_group_id': 1}]
        self.bot.handlers.db.execute.return_value = mock_db_result
        
        handle_package(self.bot, self.user_id, package)
        
        # Check that the user group was created
        self.bot.handlers.db.execute.assert_called()
        # Check that questions were scheduled
        self.bot.handlers.schedule_questions.assert_called_with(1, 1)
        # Check that the confirmation message was sent
        self.bot.send_message.assert_called_with(
            self.user_id, 
            "Hello, Test User!\nYou have registered for: 1 month",
            reply_markup=MagicMock()  # ReplyKeyboardRemove mock
        )
        # Check that the state was cleared
        self.assertNotIn(self.user_id, self.bot.handlers.user_states)
    
    @patch('src.bot.handlers.user_states', {12345: {'state': 'awaiting_package'}})
    def test_handle_package_invalid(self):
        """Test the package handler with an invalid package."""
        package = "invalid package"
        
        handle_package(self.bot, self.user_id, package)
        
        # Check that an error message was sent
        self.bot.send_message.assert_called_with(
            self.user_id, 
            "Invalid selection. Please choose a package:", 
            reply_markup=self.bot.handlers.get_package_options()
        )
        # Check that the state was preserved
        self.assertEqual(self.bot.handlers.user_states[self.user_id]['state'], 'awaiting_package')

if __name__ == '__main__':
    unittest.main()