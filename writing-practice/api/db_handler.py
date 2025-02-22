import boto3
import os
from datetime import datetime
import json

class DynamoDBHandler:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.table_name = os.getenv('DYNAMODB_TABLE', 'kana-practice-history')
        self.table = self.dynamodb.Table(self.table_name)

    def save_attempt(self, user_id, kana, predicted_kana, confidence_score):
        """Save a practice attempt to DynamoDB."""
        try:
            item = {
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'kana': kana,
                'predicted_kana': predicted_kana,
                'confidence_score': confidence_score
            }
            
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"Error saving to DynamoDB: {str(e)}")
            return False

    def get_user_history(self, user_id, limit=10):
        """Retrieve user's practice history."""
        try:
            response = self.table.query(
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                ScanIndexForward=False,  # Sort in descending order
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error retrieving from DynamoDB: {str(e)}")
            return []