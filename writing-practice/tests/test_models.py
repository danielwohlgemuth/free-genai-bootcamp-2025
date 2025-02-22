import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image
import io
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.kana_recognition import KanaRecognitionModel

class TestKanaRecognitionModel(unittest.TestCase):
    def setUp(self):
        self.model = KanaRecognitionModel()
        
        # Create a simple test image
        self.test_image = Image.new('L', (28, 28), color=255)
        
    def test_preprocess_image_numpy(self):
        """Test image preprocessing with numpy array input"""
        image_array = np.array(self.test_image)
        processed = self.model.preprocess_image(image_array)
        
        self.assertIsInstance(processed, list)
        self.assertEqual(len(processed), 1)  # Batch size
        self.assertEqual(len(processed[0]), 28)  # Height
        self.assertEqual(len(processed[0][0]), 28)  # Width
        self.assertEqual(len(processed[0][0][0]), 1)  # Channels

    @patch('boto3.client')
    def test_predict(self, mock_boto3_client):
        """Test model prediction with mocked AWS response"""
        # Mock SageMaker response
        mock_response = {
            'Body': io.BytesIO(json.dumps({
                'predictions': [{'class': 'あ', 'confidence': 0.95}]
            }).encode())
        }
        mock_boto3_client.return_value.invoke_endpoint.return_value = mock_response
        
        # Test prediction
        result = self.model.predict(self.test_image)
        self.assertEqual(result['class'], 'あ')
        self.assertEqual(result['confidence'], 0.95)

if __name__ == '__main__':
    unittest.main()