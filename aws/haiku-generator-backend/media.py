import base64
import boto3
import io
import json
import os
from database import update_translation, update_image_description, update_haiku_link
from dotenv import load_dotenv
from langchain_aws import BedrockLLM
from PIL import Image
from storage import upload_file


load_dotenv()


MODEL_REGION = os.getenv('MODEL_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
LLM_MODEL_PROVIDER = os.getenv('LLM_MODEL_PROVIDER', 'amazon')
LLM_MODEL_ID = os.getenv('LLM_MODEL_ID')
IMAGE_MODEL_ID = os.getenv('IMAGE_MODEL_ID')


model = BedrockLLM(
    region=MODEL_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    provider=LLM_MODEL_PROVIDER,
    model_id=LLM_MODEL_ID
)

bedrock = boto3.client(service_name='bedrock-runtime')
polly = boto3.client('polly')

def generate_image(user_id: str, haiku_id: str, description: str, image_number: int):
    file_path = f"{user_id}/{haiku_id}/image-{image_number}.png"
    try:
        # Prepare the request body
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": description
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 512,
                "width": 512,
                "quality": "standard",
                "cfgScale": 8.0
            }
        })
        
        # Invoke the Bedrock model
        response = bedrock.invoke_model(
            body=body,
            modelId=IMAGE_MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        
        # Process the response
        response_body = json.loads(response.get("body").read())
        if not response_body.get("images"):
            raise ValueError("No images returned in response")
            
        base64_image = response_body["images"][0]
        
        # Convert base64 to bytes
        image_bytes = base64.b64decode(base64_image)
        image_bytes_length = len(image_bytes)
        
        # Create a BytesIO object for the image
        image_content = io.BytesIO(image_bytes)
        
        # Upload the image
        upload_file(user_id, image_content, image_bytes_length, file_path)
        update_haiku_link(user_id, haiku_id, image_number, image_link=file_path)
        return file_path
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def generate_audio(user_id: str, haiku_id: str, text: str, audio_number: int):
    storage_file_path = f"{user_id}/{haiku_id}/audio-{audio_number}.mp3"
    try:
        # Get the audio stream from Polly
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Mizuki',
            LanguageCode='ja-JP'
        )
        
        # Read the audio stream directly
        audio_content = io.BytesIO()
        audio_content.write(response['AudioStream'].read())
        audio_content_length = len(audio_content.getvalue())
        audio_content.seek(0)
        
        # Upload the audio file
        upload_file(user_id, audio_content, audio_content_length, storage_file_path)
        update_haiku_link(user_id, haiku_id, audio_number, audio_link=storage_file_path)
        return storage_file_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def generate_image_description(user_id: str, haiku_id: str, topic: str, haiku_line: str, line_number: int):
    prompt = f"""
    Generate a clear, concise image description for a haiku line that will be used to create an image.
    
    The description should:
    1. Be specific and concrete
    2. Describe the main elements and their relationships
    3. Include colors and lighting conditions
    4. Be suitable for image generation
    5. Not include any text or words in the description
    6. Focus on the key visual elements that capture the haiku's essence
    7. Format the response as a single paragraph of clear, descriptive text
    
    Original haiku line: {haiku_line}
    Topic: {topic}
    """
    description = model.invoke(prompt)
    update_image_description(user_id, haiku_id, description, line_number)
    return description

def generate_translation(user_id: str, haiku_id: str, topic: str, haiku_line: str, line_number: int):
    prompt = f"""
    Translate the following English haiku line into Japanese, maintaining the haiku structure and poetic essence:
    
    Original line: {haiku_line}
    
    Instructions:
    1. Provide only the Japanese translation
    2. Maintain the haiku's poetic quality and meaning
    3. Keep the translation concise and focused on the imagery
    4. Use natural Japanese phrasing that captures the essence of the original
    5. Format the response as a single line of Japanese text only
    
    Topic: {topic}
    """
    translation = model.invoke(prompt)
    update_translation(user_id, haiku_id, translation, line_number)
    return translation
