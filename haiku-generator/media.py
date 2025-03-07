import os
import torch
from database import retrieve_haiku_line_by_id_and_line_number, update_translation, update_image_description, update_haiku_links
from diffusers import StableDiffusionPipeline
from minio import Minio
from TTS.api import TTS


HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)
MINIO_URL = os.getenv("MINIO_URL", "http://localhost:9000")
BUCKET_NAME = os.getenv("BUCKET_NAME", "haiku")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", None)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", None)


pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)
minio_client = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)


def create_bucket_if_not_exists():
    try:
        minio_client.make_bucket(BUCKET_NAME)
    except Exception as e:
        print(f"Bucket {BUCKET_NAME} already exists or could not be created: {e}")

create_bucket_if_not_exists()

def upload_to_minio(file_path: str, object_name: str):
    minio_client.fput_object(BUCKET_NAME, object_name, file_path)

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
    update_haiku_links(haiku_id, object_url, None, image_number=image_number)

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
    update_haiku_links(haiku_id, None, object_url, audio_number=audio_number)

async def generate_image_description(haiku_id: str, haiku_line: str, line_number: int):
    description = f'An artistic representation of the haiku: {haiku_line}'
    await update_image_description(haiku_id, description, line_number)
    await generate_image(description, haiku_id, line_number)

async def generate_audio_translation(haiku_id: str, haiku_line: str, line_number: int):
    translated_haiku = await translate_haiku(haiku_line)
    await update_translation(haiku_id, translated_haiku, line_number)
    await generate_audio(translated_haiku, haiku_id, line_number)

async def translate_haiku(haiku: str):
    prompt = f'Translate the following haiku into Japanese: {haiku}'
    translation = await ollama_model.generate(prompt)
    return translation

async def generate_multimedia(haiku_id: str):
    for i in range(1, 4):
        haiku_line = await retrieve_haiku_line_by_id_and_line_number(haiku_id, i)
        await generate_image_description(haiku_id, haiku_line, i)
        await generate_audio_translation(haiku_id, haiku_line, i)
