import gradio as gr
import json
import logging
from pathlib import Path
import os
from dotenv import load_dotenv
import numpy as np
from models.kana_recognition import KanaRecognitionModel
from api.db_handler import DynamoDBHandler
from utils.rate_limiter import rate_limit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize models and handlers
def get_aws_client():
    return boto3.client('dynamodb',
                       aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                       aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                       region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Load Kana Groups
def load_kana_groups():
    with open('data/kana_groups.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Initialize global objects
kana_model = KanaRecognitionModel()
db_handler = DynamoDBHandler()

# State Management
class UserState:
    def __init__(self):
        self.current_kana = None
        self.current_group = None
        self.user_id = "anonymous"  # TODO: Implement user authentication

user_state = UserState()

def get_random_kana(group_name):
    """Get a random kana from the selected group."""
    kana_groups = load_kana_groups()
    if group_name in kana_groups:
        user_state.current_group = group_name
        user_state.current_kana = np.random.choice(kana_groups[group_name])
        return user_state.current_kana
    return None

def update_kana(group):
    """Update the current kana to practice."""
    kana = get_random_kana(group)
    return kana if kana else "Invalid group selected"

# Canvas Drawing Handler
@rate_limit
def process_drawing(image, selected_group):
    if image is None:
        return "Please draw something first!"
    
    try:
        # Get prediction from model
        prediction = kana_model.predict(image)
        if prediction is None:
            return "Error processing image. Please try again."
        
        # Extract prediction results
        predicted_kana = prediction['class']
        confidence = prediction['confidence']
        
        # Save attempt to DynamoDB
        db_handler.save_attempt(
            user_id="anonymous",  # TODO: Implement user management
            kana=selected_group,
            predicted_kana=predicted_kana,
            confidence_score=confidence
        )
        
        # Format response
        return f"Predicted: {predicted_kana}\nConfidence: {confidence:.2%}"
    except Exception as e:
        return f"Error: {str(e)}"

# Main Interface
def load_user_stats(user_id="anonymous"):
    """Load user practice statistics."""
    try:
        history = db_handler.get_user_history(user_id)
        total_attempts = len(history)
        if total_attempts == 0:
            return "No practice history yet."
        
        correct_attempts = sum(1 for h in history 
                             if h['kana'] == h['predicted_kana'])
        accuracy = (correct_attempts / total_attempts) * 100
        
        return f"Total Attempts: {total_attempts}\nCorrect: {correct_attempts}\nAccuracy: {accuracy:.1f}%"
    except Exception as e:
        logger.error(f"Error loading user stats: {str(e)}")
        return "Error loading statistics"

def create_interface():
    kana_groups = load_kana_groups()
    
    with gr.Blocks() as interface:
        gr.Markdown("# Japanese Kana Writing Practice")
        
        with gr.Row():
            with gr.Column():
                # Kana group selection
                group_select = gr.Dropdown(
                    choices=list(kana_groups.keys()),
                    label="Select Kana Group",
                    value=list(kana_groups.keys())[0]
                )
                
                # Display current kana
                current_kana = gr.Textbox(label="Current Kana", interactive=False)
            
            with gr.Column():
                # Drawing canvas
                canvas = gr.Image(source="canvas", tool="sketch", 
                                shape=(400, 400), 
                                image_mode="L")
                
                # Submit button
                submit_btn = gr.Button("Submit")
                
                # Result display
                result = gr.Textbox(label="Result")
                
                # Statistics display
                stats_btn = gr.Button("Show Statistics")
                stats_display = gr.Textbox(label="Practice Statistics", 
                                         interactive=False)
        
        # Event handlers
        submit_btn.click(
            fn=process_drawing,
            inputs=[canvas, group_select],
            outputs=[result]
        )
        
        group_select.change(
            fn=update_kana,
            inputs=[group_select],
            outputs=[current_kana]
        )
        
        # Statistics button handler
        stats_btn.click(
            fn=load_user_stats,
            inputs=[],
            outputs=[stats_display]
        )
        
        # Initialize with first kana
        update_kana(list(kana_groups.keys())[0])
    
    return interface

if __name__ == "__main__":
    try:
        logger.info("Starting Kana Writing Practice application...")
        interface = create_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=int(os.getenv("PORT", 7860)),
            show_error=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise