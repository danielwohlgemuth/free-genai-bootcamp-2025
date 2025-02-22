import numpy as np
from PIL import Image
import boto3
import os
import io
import base64

class KanaRecognitionModel:
    def __init__(self):
        self.sagemaker_runtime = boto3.client('sagemaker-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.endpoint_name = os.getenv('SAGEMAKER_ENDPOINT', 'kana-recognition-endpoint')

    def preprocess_image(self, image):
        """Convert and preprocess the image for model input."""
        if isinstance(image, str) and image.startswith('data:image'):
            # Handle base64 image
            image = Image.open(io.BytesIO(base64.b64decode(image.split(',')[1])))
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Convert to grayscale and resize
        image = image.convert('L').resize((28, 28))
        
        # Normalize pixel values
        image_array = np.array(image) / 255.0
        return image_array.reshape(1, 28, 28, 1).tolist()

    def predict(self, image):
        """Send the preprocessed image to SageMaker endpoint for inference."""
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Convert to JSON string
            payload = json.dumps({'instances': processed_image})
            
            # Get prediction from SageMaker endpoint
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=payload
            )
            
            # Parse response
            result = json.loads(response['Body'].read().decode())
            return result['predictions'][0]
            
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            return None