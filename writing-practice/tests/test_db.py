import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.db_handler import DynamoDBHandler

class TestDynamoDBHandler(unittest.TestCase):
    def setUp(self):
        self.db_handler = DynamoDBHandler()
        
    @patch('boto3.resource')
    def test_save_attempt(self, mock_boto3_resource):
        """Test saving practice attempt"""
        mock_table = MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        
        result = self.db_handler.save_attempt(
            user_id="test_user",
            kana="あ",
            predicted_kana="あ",
            confidence_score=0.95
        )
        
        self.assertTrue(result)
        mock_table.put_item.assert_called_once()
        
    @patch('boto3.resource')
    def test_get_user_history(self, mock_boto3_resource):
        """Test retrieving user history"""
        mock_table = MagicMock()
        mock_items = [
            {
                'user_id': 'test_user',
                'kana': 'あ',
                'predicted_kana': 'あ',
                'confidence_score': 0.95
            }
        ]
        mock_table.query.return_value = {'Items': mock_items}
        mock_boto3_resource.return_value.Table.return_value = mock_table
        
        history = self.db_handler.get_user_history("test_user")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['kana'], 'あ')

if __name__ == '__main__':
    unittest.main()