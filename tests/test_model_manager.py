"""
Unit tests for ModelManager.
"""
import unittest
from unittest.mock import Mock, patch
from src.models.model_manager import ModelManager

class TestModelManager(unittest.TestCase):
    """Test cases for ModelManager."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.manager = ModelManager()
    
    def test_load_config(self):
        """Test configuration loading."""
        config = self.manager.config
        self.assertIsNotNone(config)
        self.assertIn('model', config)
        self.assertIn('generation', config)
    
    @patch('src.models.model_manager.AutoModelForCausalLM')
    @patch('src.models.model_manager.AutoTokenizer')
    def test_load_model(self, mock_tokenizer, mock_model):
        """Test model loading."""
        result = self.manager.load_model()
        self.assertTrue(result)
        self.assertTrue(self.manager.is_loaded)

if __name__ == '__main__':
    unittest.main()
