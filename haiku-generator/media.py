import os
import sqlite3
import torch
from diffusers import StableDiffusionPipeline
from minio import Minio
from TTS.api import TTS
from database import get_db_connection


HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)
MINIO_URL = "http://localhost:9000"
BUCKET_NAME = "haiku"
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

def upload_to_minio(file_path: str, object_name: str):
    minio_client.fput_object(BUCKET_NAME, object_name, file_path)

def update_haiku_links(haiku_id: str, image_link: str, audio_link: str, image_number: int = None, audio_number: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if image_number is not None:
        cursor.execute(f'''UPDATE haiku SET image_link_{image_number} = ? WHERE haiku_id = ?''', (image_link, haiku_id))
    if audio_number is not None:
        cursor.execute(f'''UPDATE haiku SET audio_link_{audio_number} = ? WHERE haiku_id = ?''', (audio_link, haiku_id))
    conn.commit()
    conn.close()

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


async def create_image_description(haiku: str):
    return f'An artistic representation of the haiku: {haiku}'

async def generate_image(haiku_id: str, haiku_line: str, line_number: int):
    description = await create_image_description(haiku_line)
    await update_image_description_in_db(haiku_id, description, line_number)
    await generate_image_from_description(description)

async def generate_audio(haiku_id: str, haiku_line: str, line_number: int):
    translated_haiku = await translate_haiku(haiku_line)
    await update_translation_in_db(haiku_id, translated_haiku, line_number)
    await generate_audio_from_text(translated_haiku)

async def translate_haiku(haiku: str):
    try:
        prompt = f'Translate the following haiku into Japanese: {haiku}'
        translation = await ollama_model.generate(prompt)
        logging.info(f"Haiku translated: {translation}")
        return translation
    except Exception as e:
        logging.error(f"Error translating haiku: {e}")
        raise

async def generate_multimedia(haiku_id: str):
    for i in range(1, 4):
        haiku_line = await retrieve_haiku_line(haiku_id, i)
        await generate_image(haiku_id, haiku_line, i)
        await generate_audio(haiku_id, haiku_line, i)

async def retrieve_haiku_line(haiku_id: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT haiku_line_en_{line_number} FROM haiku WHERE haiku_id = ?', (haiku_id,))
    line = cursor.fetchone()[0]
    conn.close()
    return line

async def update_translation_in_db(haiku_id: str, translated_haiku: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET haiku_line_ja_{line_number} = ? WHERE haiku_id = ?', (translated_haiku, haiku_id))
    conn.commit()
    conn.close()

async def update_image_description_in_db(haiku_id: str, description: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET image_description_{line_number} = ? WHERE haiku_id = ?', (description, haiku_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_bucket_if_not_exists()
