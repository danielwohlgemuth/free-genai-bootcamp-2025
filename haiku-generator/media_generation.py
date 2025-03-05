import torch
from diffusers import StableDiffusionPipeline
from TTS.api import TTS
import os
import requests
from minio import Minio
import sqlite3

# Set up Stable Diffusion
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)
pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)

# MinIO configuration
MINIO_URL = "http://localhost:9000"
BUCKET_NAME = "haiku"
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", None)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", None)

# Initialize MinIO client
minio_client = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

# Function to create MinIO bucket if it does not exist
def create_bucket_if_not_exists():
    try:
        minio_client.make_bucket(BUCKET_NAME)
    except Exception as e:
        print(f"Bucket {BUCKET_NAME} already exists or could not be created: {e}")

# Call the function to ensure the bucket is created at startup
create_bucket_if_not_exists()

# Function to upload file to MinIO
def upload_to_minio(file_path: str, object_name: str):
    minio_client.fput_object(BUCKET_NAME, object_name, file_path)

# Function to update haiku record in the database
def update_haiku_links(haiku_id: str, image_link: str, audio_link: str, image_number: int = None, audio_number: int = None):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    if image_number is not None:
        cursor.execute(f'''UPDATE haiku SET image_link_{image_number} = ? WHERE haiku_id = ?''', (image_link, haiku_id))
    if audio_number is not None:
        cursor.execute(f'''UPDATE haiku SET audio_link_{audio_number} = ? WHERE haiku_id = ?''', (audio_link, haiku_id))
    conn.commit()
    conn.close()

# Function to generate image from haiku description
async def generate_image(description: str, haiku_id: str, image_number: int):
    image = pipe(
        description,
        num_inference_steps=10,
        guidance_scale=5.0,
    ).images[0]
    image_file_path = f"haiku/{haiku_id}/image-{image_number}.png"
    image.save(image_file_path)
    upload_to_minio(image_file_path, f"{haiku_id}/image-{image_number}.png")
    object_url = f"{MINIO_URL}/{BUCKET_NAME}/{haiku_id}/image-{image_number}.png"
    # Update image link in database
    update_haiku_links(haiku_id, object_url, None, image_number=image_number)

# Function to generate audio from text
async def generate_audio(text: str, haiku_id: str, audio_number: int):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    audio_file_path = f"haiku/{haiku_id}/audio-{audio_number}.wav"
    tts.tts_to_file(
        text=text,
        speaker="Chandra MacFarland",
        language="ja",
        file_path=audio_file_path
    )
    upload_to_minio(audio_file_path, f"{haiku_id}/audio-{audio_number}.wav")
    object_url = f"{MINIO_URL}/{BUCKET_NAME}/{haiku_id}/audio-{audio_number}.wav"
    # Update audio link in database
    update_haiku_links(haiku_id, None, object_url, audio_number=audio_number)
