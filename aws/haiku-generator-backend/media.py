import boto3
import io
import os
import torch
from database import update_translation, update_image_description, update_haiku_link
from diffusers import AmusedPipeline
from dotenv import load_dotenv
from langchain_aws import BedrockLLM
from storage import upload_file


load_dotenv()
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)

polly = boto3.client('polly')

model = BedrockLLM(
    # base_url=MODEL_BASE_URL,
    # model=MODEL_NAME,
    credentials_profile_name="bedrock-admin",
    provider="cohere",
    model_id="amazon.titan-text-express-v1"
)
# pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)
pipe = AmusedPipeline.from_pretrained("amused/amused-256", token=HUGGINGFACEHUB_API_TOKEN)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)


def generate_image(haiku_id: str, description: str, image_number: int):
    image = pipe(
        description,
        num_inference_steps=5,
        guidance_scale=5.0,
    ).images[0]
    file_path = f"{haiku_id}/image-{image_number}.png"
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes_length = len(image_bytes.getvalue())
    image_bytes.seek(0)
    upload_file(image_bytes, image_bytes_length, file_path)
    update_haiku_link(haiku_id, image_number, image_link=file_path)
    return file_path

def generate_audio(haiku_id: str, text: str, audio_number: int):
    storage_file_path = f"{haiku_id}/audio-{audio_number}.wav"
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
        upload_file(audio_content, audio_content_length, storage_file_path)
        update_haiku_link(haiku_id, audio_number, audio_link=storage_file_path)
        return storage_file_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def generate_image_description(haiku_id: str, topic: str, haiku_line: str, line_number: int):
    prompt = f"""Generate a high-contrast image with a plain background.
    The subject should be clear and well-defined, avoiding visual noise or excessive details.
    Colors should be bold and distinct to ensure strong visibility.
    Do not include any text in the image.
    Only provide the description needed to generate the image. No additional text.
    Topic: {topic}
    Sentence: {haiku_line}"""
    description = model.invoke(prompt)
    update_image_description(haiku_id, description, line_number)
    return description

def generate_translation(haiku_id: str, topic: str, haiku_line: str, line_number: int):
    prompt = f"""Translate the sentence into Japanese
    If the sentence cannot be translated directly, provide the closest equivalent translation.
    Only return the Japanese translation. Do not add any additional text.
    Topic: {topic}
    Sentence: {haiku_line}"""
    translation = model.invoke(prompt)
    update_translation(haiku_id, translation, line_number)
    return translation
