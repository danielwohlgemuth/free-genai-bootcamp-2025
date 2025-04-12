import base64
import boto3
import io
import json
from database import update_translation, update_image_description, update_haiku_link
from dotenv import load_dotenv
from langchain_aws import BedrockLLM
from PIL import Image
from storage import upload_file


load_dotenv()

bedrock = boto3.client(service_name='bedrock-runtime')
polly = boto3.client('polly')

model = BedrockLLM(
    provider="cohere",
    model_id="amazon.titan-text-express-v1"
)


def generate_image(user_id: str, haiku_id: str, description: str, image_number: int):
    file_path = f"{user_id}/{haiku_id}/image-{image_number}.png"
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": description,
            "controlMode": "CANNY_EDGE",
            "controlStrength": 0.7
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 512,
            "width": 512,
            "cfgScale": 8.0
        }
    })
    
    response = bedrock.invoke_model(
        body=body, modelId="us.anthropic.claude-3-haiku-20240307-v1:0", accept="application/json", contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())

    base64_image = response_body.get("images")[0]
    base64_bytes = base64_image.encode('ascii')
    image_bytes = base64.b64decode(base64_bytes)

    finish_reason = response_body.get("error")

    image = Image.open(io.BytesIO(image_bytes))

    image_bytes_length = len(image_bytes.getvalue())
    image_bytes.seek(0)
    upload_file(user_id, image_bytes, image_bytes_length, file_path)
    update_haiku_link(user_id, haiku_id, image_number, image_link=file_path)
    return file_path

def generate_audio(user_id: str, haiku_id: str, text: str, audio_number: int):
    storage_file_path = f"{user_id}/{haiku_id}/audio-{audio_number}.wav"
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Mizuki',
            LanguageCode='ja-JP'
        )
        
        # Create a temporary file to store the audio
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(response['AudioStream'].read())
        temp_file.close()
        
        audio_content = io.BytesIO(temp_file.read())
        audio_content_length = len(audio_content.getvalue())
        audio_content.seek(0)
        upload_file(user_id, audio_content, audio_content_length, storage_file_path)
        update_haiku_link(user_id, haiku_id, audio_number, audio_link=storage_file_path)
        return storage_file_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def generate_image_description(user_id: str, haiku_id: str, topic: str, haiku_line: str, line_number: int):
    prompt = f"""Generate a high-contrast image with a plain background.
    The subject should be clear and well-defined, avoiding visual noise or excessive details.
    Colors should be bold and distinct to ensure strong visibility.
    Do not include any text in the image.
    Only provide the description needed to generate the image. No additional text.
    Topic: {topic}
    Sentence: {haiku_line}"""
    description = model.invoke(prompt)
    update_image_description(user_id, haiku_id, description, line_number)
    return description

def generate_translation(user_id: str, haiku_id: str, topic: str, haiku_line: str, line_number: int):
    prompt = f"""Translate the sentence into Japanese
    If the sentence cannot be translated directly, provide the closest equivalent translation.
    Only return the Japanese translation. Do not add any additional text.
    Topic: {topic}
    Sentence: {haiku_line}"""
    translation = model.invoke(prompt)
    update_translation(user_id, haiku_id, translation, line_number)
    return translation
