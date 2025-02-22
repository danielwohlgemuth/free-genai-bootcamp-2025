import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import load_kana_groups, process_drawing
from models.kana_recognition import KanaRecognitionModel
from api.db_handler import DynamoDBHandler

class TestApp(unittest.TestCase):
    def setUp(self):
        self.mock_kana_model = MagicMock(spec=KanaRecognitionModel)
        self.mock_db_handler = MagicMock(spec=DynamoDBHandler)

    def test_load_kana_groups(self):
        """Test loading kana groups from JSON file"""
        groups = load_kana_groups()
        self.assertIsInstance(groups, dict)
        self.assertTrue(len(groups) > 0)
        self.assertIn("Hiragana Basic", groups)

    @patch('app.kana_model')
    @patch('app.db_handler')
    def test_process_drawing_success(self, mock_db, mock_model):
        """Test successful drawing processing"""
        # Mock the model prediction
        mock_model.predict.return_value = {
            'class': 'あ',
            'confidence': 0.95
        }
        
        # Mock DB save
        mock_db.save_attempt.return_value = True
        
        # Test processing
        result = process_drawing(MagicMock(), "Hiragana Basic")
        self.assertIn("Predicted: あ", result)
        self.assertIn("Confidence: 95.00%", result)

    def test_process_drawing_no_image(self):
        """Test drawing processing with no image"""
        result = process_drawing(None, "Hiragana Basic")
        self.assertEqual(result, "Please draw something first!")

if __name__ == '__main__':
    unittest.main()