import io
import os
import torch
from database import update_translation, update_image_description, update_haiku_link
from diffusers import StableDiffusion3Pipeline
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from storage import upload_file
from TTS.api import TTS


load_dotenv()
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)


model = OllamaLLM(
    base_url=MODEL_BASE_URL,
    model=MODEL_NAME
)
pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")


def generate_image(description: str, haiku_id: str, image_number: int):
    image = pipe(
        description,
        num_inference_steps=5,
        guidance_scale=5.0,
    ).images[0]
    file_path = f"{haiku_id}/image-{image_number}.png"
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    upload_file(image_bytes, file_path)
    update_haiku_link(haiku_id, image_link=file_path, number=image_number)
    return file_path

def generate_audio(text: str, haiku_id: str, audio_number: int):
    file_path = f"{haiku_id}/audio-{audio_number}.wav"
    audio_bytes = io.BytesIO()
    tts.tts_to_file(
        text=text,
        speaker="Chandra MacFarland",
        language="ja",
        pipe_out=audio_bytes.getbuffer()
    )
    audio_bytes.seek(0)
    upload_file(audio_bytes, file_path)
    update_haiku_link(haiku_id, audio_link=file_path, number=audio_number)
    return file_path

def generate_image_description(haiku_id: str, haiku_line: str, line_number: int):
    description = f'An artistic representation of the haiku: {haiku_line}'
    update_image_description(haiku_id, description, line_number)
    return description

def generate_audio_translation(haiku_id: str, haiku_line: str, line_number: int):
    prompt = f'Translate the following haiku into Japanese: {haiku_line}'
    translation = model.invoke(prompt)
    update_translation(haiku_id, translation, line_number)
    return translation
