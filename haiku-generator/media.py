import os
import torch
from database import update_translation, update_image_description, update_haiku_links
from diffusers import StableDiffusionPipeline
from langchain_ollama import OllamaLLM
from storage import upload_file
from TTS.api import TTS


MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)


model = OllamaLLM(model=MODEL_NAME)
pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")


def generate_image(description: str, haiku_id: str, image_number: int):
    image = pipe(
        description,
        num_inference_steps=10,
        guidance_scale=5.0,
    ).images[0]
    image_file_path = f"{haiku_id}/image-{image_number}.png"
    image.save(image_file_path)
    upload_file(image_file_path, f"image-{image_number}.png")
    update_haiku_links(haiku_id, image_file_path, None, image_number=image_number)
    return image_file_path

def generate_audio(text: str, haiku_id: str, audio_number: int):
    audio_file_path = f"{haiku_id}/audio-{audio_number}.wav"
    tts.tts_to_file(
        text=text,
        speaker="Chandra MacFarland",
        language="ja",
        file_path=audio_file_path
    )
    upload_file(audio_file_path, f"audio-{audio_number}.wav")
    update_haiku_links(haiku_id, None, audio_file_path, audio_number=audio_number)
    return audio_file_path

def generate_image_description(haiku_id: str, haiku_line: str, line_number: int):
    description = f'An artistic representation of the haiku: {haiku_line}'
    update_image_description(haiku_id, description, line_number)
    return description

def generate_audio_translation(haiku_id: str, haiku_line: str, line_number: int):
    prompt = f'Translate the following haiku into Japanese: {haiku_line}'
    translation = model.invoke(prompt)
    update_translation(haiku_id, translation, line_number)
    return translation
