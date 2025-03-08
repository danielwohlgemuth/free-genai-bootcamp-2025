import os
import torch
from database import update_translation, update_image_description, update_haiku_links
from diffusers import StableDiffusionPipeline
from graph import define_workflow
from langchain_ollama import OllamaLLM
from minio import Minio
from TTS.api import TTS


MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)
MINIO_URL = os.getenv("MINIO_URL", "http://localhost:9000")
BUCKET_NAME = os.getenv("BUCKET_NAME", "haiku")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", None)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", None)


model = OllamaLLM(model=MODEL_NAME)
pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)
minio_client = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
workflow = define_workflow()

def create_bucket_if_not_exists():
    try:
        minio_client.make_bucket(BUCKET_NAME)
    except Exception as e:
        print(f"Bucket {BUCKET_NAME} already exists or could not be created: {e}")

create_bucket_if_not_exists()

def upload_to_minio(file_path: str, object_name: str):
    minio_client.fput_object(BUCKET_NAME, object_name, file_path)

def generate_image(description: str, haiku_id: str, image_number: int):
    image = pipe(
        description,
        num_inference_steps=10,
        guidance_scale=5.0,
    ).images[0]
    image_file_path = f"{haiku_id}/image-{image_number}.png"
    image.save(image_file_path)
    upload_to_minio(image_file_path, f"image-{image_number}.png")
    object_url = f"{MINIO_URL}/{BUCKET_NAME}/{image_file_path}"
    update_haiku_links(haiku_id, object_url, None, image_number=image_number)
    return object_url

def generate_audio(text: str, haiku_id: str, audio_number: int):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    audio_file_path = f"{haiku_id}/audio-{audio_number}.wav"
    tts.tts_to_file(
        text=text,
        speaker="Chandra MacFarland",
        language="ja",
        file_path=audio_file_path
    )
    upload_to_minio(audio_file_path, f"audio-{audio_number}.wav")
    object_url = f"{MINIO_URL}/{BUCKET_NAME}/{audio_file_path}"
    update_haiku_links(haiku_id, None, object_url, audio_number=audio_number)
    return object_url

def generate_image_description(haiku_id: str, haiku_line: str, line_number: int):
    description = f'An artistic representation of the haiku: {haiku_line}'
    update_image_description(haiku_id, description, line_number)
    return description

def generate_audio_translation(haiku_id: str, haiku_line: str, line_number: int):
    prompt = f'Translate the following haiku into Japanese: {haiku_line}'
    translation = model.invoke(prompt)
    update_translation(haiku_id, translation, line_number)
    return translation

def generate_media(haiku_id: str):
    workflow.invoke({"haiku_id": haiku_id})
