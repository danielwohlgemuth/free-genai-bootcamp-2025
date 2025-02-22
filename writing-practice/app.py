import os
import json
import gradio as gr
import boto3
from dotenv import load_dotenv
from manga_ocr import MangaOcr
from PIL import Image
import io
import requests
from pathlib import Path
import logging
from pythonjsonlogger import jsonlogger

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# AWS clients
bedrock = boto3.client('bedrock-runtime')
polly = boto3.client('polly')

# Initialize Manga OCR
ocr = MangaOcr()

# Cache for audio and kana representations
audio_cache = {}
kana_cache = {}

# Backend URL configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def fetch_groups():
    """Fetch available word groups from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/groups")
        response.raise_for_status()
        groups = response.json()['items']
        return [(group['name'], group['id']) for group in groups]
    except requests.RequestException as e:
        logger.error(f"Error fetching groups: {str(e)}")
        return []

def fetch_words(group_id):
    """Fetch words for a specific group"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/groups/{group_id}/words")
        response.raise_for_status()
        return response.json()['items']
    except requests.RequestException as e:
        logger.error(f"Error fetching words: {str(e)}")
        return []

def generate_kana(text):
    """Generate kana representation using AWS Bedrock"""
    if text in kana_cache:
        return kana_cache[text]
    
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps({
                "prompt": f"Convert this English text to Japanese kana: {text}",
                "max_tokens": 100
            })
        )
        kana = json.loads(response['body'].read())['completion']
        kana_cache[text] = kana
        return kana
    except Exception as e:
        logger.error(f"Error generating kana: {str(e)}")
        return None

def generate_audio(text):
    """Generate audio using Amazon Polly"""
    if text in audio_cache:
        return audio_cache[text]
    
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Mizuki',
            LanguageCode='ja-JP'
        )
        
        audio_stream = io.BytesIO(response['AudioStream'].read())
        audio_cache[text] = audio_stream
        return audio_stream
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return None

def process_drawing(image):
    """Process the drawing using Manga OCR"""
    try:
        # Convert gradio image to PIL Image
        if isinstance(image, str):
            image = Image.open(image)
        
        # Perform OCR
        text = ocr(image)
        return text
    except Exception as e:
        logger.error(f"Error processing drawing: {str(e)}")
        return None

def validate_input(drawing, target_kana):
    """Validate user input against target kana"""
    if drawing is None:
        return "Please draw something first!"
    
    recognized_text = process_drawing(drawing)
    if recognized_text is None:
        return "Error processing your drawing. Please try again."
    
    if recognized_text.strip() == target_kana.strip():
        return "Correct! Well done!"
    else:
        return f"Not quite right. Expected {target_kana}, got {recognized_text}. Try again!"

# Gradio Interface
def create_interface():
    with gr.Blocks() as app:
        current_word = gr.State({})
        
        with gr.Row():
            group_dropdown = gr.Dropdown(
                choices=fetch_groups(),
                label="Select Word Group",
                interactive=True
            )
        
        with gr.Row():
            english_text = gr.Text(label="English Word", interactive=False)
            kana_text = gr.Text(label="Kana", interactive=False)
        
        with gr.Row():
            canvas = gr.Image(
                source="canvas",
                tool="sketch",
                shape=(300, 900),
                label="Draw here"
            )
        
        with gr.Row():
            clear_btn = gr.Button("Clear Canvas")
            submit_btn = gr.Button("Submit")
            next_word_btn = gr.Button("Next Word")
        
        with gr.Row():
            audio_player = gr.Audio(
                label="Pronunciation",
                interactive=False,
                visible=False
            )
            result_text = gr.Text(label="Result")
        
        def load_new_word(group_id):
            if not group_id:
                return {}, "", "", None, gr.Audio.update(visible=False)
            
            words = fetch_words(group_id)
            if not words:
                return {}, "", "", None, gr.Audio.update(visible=False)
            
            # Select first word for now (could be randomized)
            word = words[0]
            kana = generate_kana(word['english'])
            audio = generate_audio(word['japanese'])
            
            return (
                word,
                word['english'],
                kana,
                None,  # Clear canvas
                gr.Audio.update(value=audio, visible=True) if audio else gr.Audio.update(visible=False)
            )
        
        def submit_drawing(drawing, word):
            if not word or 'japanese' not in word:
                return "Please select a word group first!"
            return validate_input(drawing, word['japanese'])
        
        # Event handlers
        group_dropdown.change(
            load_new_word,
            inputs=[group_dropdown],
            outputs=[current_word, english_text, kana_text, canvas, audio_player]
        )
        
        next_word_btn.click(
            load_new_word,
            inputs=[group_dropdown],
            outputs=[current_word, english_text, kana_text, canvas, audio_player]
        )
        
        clear_btn.click(
            lambda: None,
            outputs=[canvas]
        )
        
        submit_btn.click(
            submit_drawing,
            inputs=[canvas, current_word],
            outputs=[result_text]
        )
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
