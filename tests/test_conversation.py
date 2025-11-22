"""
Unit tests for ConversationManager.
"""
import unittest
from src.core.conversation import ConversationManager

class TestConversationManager(unittest.TestCase):
    """Test cases for ConversationManager."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.manager = ConversationManager()
    
    def test_add_user_message(self):
        """Test adding user message."""
        self.manager.add_user_message("Hello")
        self.assertEqual(len(self.manager.messages), 1)
        self.assertEqual(self.manager.messages[0]["role"], "user")
    
    def test_add_assistant_message(self):
        """Test adding assistant message."""
        self.manager.add_assistant_message("Hi there!")
        self.assertEqual(len(self.manager.messages), 1)
        self.assertEqual(self.manager.messages[0]["role"], "assistant")
    
    def test_clear_history(self):
        """Test clearing conversation history."""
        self.manager.add_user_message("Hello")
        self.manager.add_assistant_message("Hi")
        self.manager.clear_history()
        self.assertEqual(len(self.manager.messages), 0)
    
    def test_get_message_count(self):
        """Test getting message count."""
        self.manager.add_user_message("Hello")
        self.manager.add_assistant_message("Hi")
        self.assertEqual(self.manager.get_message_count(), 2)

if __name__ == '__main__':
    unittest.main()
