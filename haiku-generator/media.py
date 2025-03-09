import io
import os
import torch
from database import update_translation, update_image_description, update_haiku_link
# from diffusers import StableDiffusion3Pipeline
from diffusers import AmusedPipeline
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from pyfakefs.fake_filesystem_unittest import Patcher
from storage import upload_file
from TTS.api import TTS
import cutlet


load_dotenv()
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)


model = OllamaLLM(
    base_url=MODEL_BASE_URL,
    model=MODEL_NAME
)
# pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)
pipe = AmusedPipeline.from_pretrained("amused/amused-256", token=HUGGINGFACEHUB_API_TOKEN)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
cutlet_path = cutlet.__file__.replace("__init__.py", "exceptions.tsv")


def generate_image(haiku_id: str, description: str, image_number: int):
    image = pipe(
        description,
        num_inference_steps=50,
        guidance_scale=5.0,
    ).images[0]
    file_path = f"{haiku_id}/image-{image_number}.png"
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes_length = len(image_bytes.getvalue())
    image_bytes.seek(0)
    upload_file(image_bytes, image_bytes_length, file_path)
    update_haiku_link(haiku_id, image_link=file_path, number=image_number)
    return file_path

def generate_audio(haiku_id: str, text: str, audio_number: int):
    file_path = f"{haiku_id}/audio-{audio_number}.wav"

    with Patcher() as patcher:
        patcher.fs.add_real_file(cutlet_path)

        patcher.fs.create_file(file_path)
        tts.tts_to_file(
            text=text,
            speaker="Chandra MacFarland",
            language="ja",
            file_path=file_path
        )
        with open(file_path, 'rb') as f:
            audio_content = io.BytesIO(f.read())
            audio_content_length = len(audio_content.getvalue())
            audio_content.seek(0)
            upload_file(audio_content, audio_content_length, file_path)
            update_haiku_link(haiku_id, audio_link=file_path, number=audio_number)
    return file_path

def generate_image_description(haiku_id: str, haiku_line: str, line_number: int):
    prompt = f"""Generate a high-contrast, minimalist image with a plain background.
    Use simple shapes and solid colors, avoiding intricate details or shading.
    The subject should be clearly distinguishable. Only provide the description. No additional text.
    Subject: {haiku_line}"""
    description = model.invoke(prompt)
    update_image_description(haiku_id, description, line_number)
    return description

def generate_audio_translation(haiku_id: str, haiku_line: str, line_number: int):
    prompt = f"""Only return the Japanese translation. Do not add any additional text.
    Translate the following haiku into Japanese: {haiku_line}"""
    translation = model.invoke(prompt)
    update_translation(haiku_id, translation, line_number)
    return translation
