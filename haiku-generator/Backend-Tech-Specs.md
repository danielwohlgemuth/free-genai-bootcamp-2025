# Haiku Generator

Generate haikus based on a topic provided by the user.

## Business Goal

provide a chatbot with which the user can interact. the chatbot will help the user pick a topic, and the chatbot will generate a haiku based on that topic in English. if the user agrees with the haiku, the chatbot will generate three images and audios, each corresponding to one line of the haiku. if the user disagrees, the chatbot will help the user refine the topic. the chatbot will have access to a tool that will generate the images and audios. The chatbot will translate the haiku into Japanese and the generated audio will be based on the Japanese version of the haiku.

## Architecture

The app will consist of an agentic workflow with two tools available: one to kick off the generation of the images and audios, and another to check if the generation has completed.

The tool to kick off the generation of the images and audios will be a function that takes the haiku as input and returns the haiku id.
For each line of the haiku, the tool will translate the line into Japanese and generate the audio based on the Japanese version of the line. It will also generate the image description and then generate the image based on the image description. To ensure consistency between the images, the description of the first image will flow into the generation of the image description for the second image, and the description of the first and second image will flow into the generation of the image description for the third image.

The mermaid diagram below shows the workflow:

```mermaid
graph TD;
	__start__([start]):::first
	generate_image_description_1(generate image_description_1)
	generate_image_description_2(generate image_description_2)
	generate_image_description_3(generate image_description_3)
	generate_image_1(generate image_1)
	generate_image_2(generate image_2)
	generate_image_3(generate image_3)
	translate_line_1(translate line_1)
	translate_line_2(translate line_2)
	translate_line_3(translate line_3)
	generate_audio_1(generate audio_1)
	generate_audio_2(generate audio_2)
	generate_audio_3(generate audio_3)
	__end__([end]):::last
	__start__ --> translate_line_1;
	__start__ --> translate_line_2;
	__start__ --> translate_line_3;
	translate_line_1 --> generate_audio_1;
	translate_line_2 --> generate_audio_2;
	translate_line_3 --> generate_audio_3;
	generate_audio_1 --> __end__;
	generate_audio_2 --> __end__;
	generate_audio_3 --> __end__;
	__start__ --> generate_image_description_1;
	generate_image_description_1 --> generate_image_description_2;
	generate_image_description_1 --> generate_image_1;
	generate_image_description_2 --> generate_image_description_3;
	generate_image_description_2 --> generate_image_2;
	generate_image_description_3 --> generate_image_3;
	generate_image_1 --> __end__;
	generate_image_2 --> __end__;
	generate_image_3 --> __end__;
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

The tool to check if the generation has completed will be a function that takes the haiku id as input and returns a response saying that it has completed, there was an error, or it is still in progress.

## Technical Specs

Use the OPEA (Open Platform for Enterprise AI) framework. The haiku generation will be considered the megaservice and the chatbot and the image and audio generation will be considered the microservices.

LangChain will be used to generate the haiku, translate it into Japanese, and call the tool to generate the images and audios and check if the generation has completed.
LangGraph will be used to build the flow that generates the images and audios.

Images will be generated using https://huggingface.co/stabilityai/stable-diffusion-3.5-medium, with low inference steps to save on compute.
It will use something like the following code

```python
import torch
from diffusers import StableDiffusion3Pipeline
import os

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)

pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)

device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)

image = pipe(
    """image prompt""",
    num_inference_steps=5,
    guidance_scale=4.5,
).images[0]
image.save(f"{STORAGE_URL}/haiku/{haiku_id}/image-1.png")
```

Audios will be generated using the coqui-tts package, with the tts_models/multilingual/multi-dataset/xtts_v2 model, the language set to Japanese, and the speaker set to Chandra MacFarland.
It will use something like the following code

```python
import torch
from TTS.api import TTS

device = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
tts.tts_to_file(
    text="japanese text",
    speaker="Chandra MacFarland",
    language="ja",
    file_path=f"{STORAGE_URL}/haiku/{haiku_id}/audio-1.wav"
)
```

The translation from English to Japanese will be done using https://huggingface.co/Qwen/Qwen2-7B. Ollama will be used to host the LLM and will be available at http://localhost:11434 by default but also configurable via environment variables.
The chatbot will also be powered by Qwen2-7B.

SQLite will be used to store information about the haiku and each row will include the following information:
- haiku id
- status ("in progress", "completed", "failed")
- error message (if any)
- haiku line 1 en
- haiku line 2 en
- haiku line 3 en
- haiku line 1 ja
- haiku line 2 ja
- haiku line 3 ja
- image description 1
- image description 2
- image description 3
- image link 1
- image link 2
- image link 3
- audio link 1
- audio link 2
- audio link 3

Column limits:
- haiku id (primary key) 36 characters uuid string provided by the frontend
- status (default "in progress") allowed values are "in progress", "completed", "failed"
- error message the error message will be limited to 1000 characters
- The lines will be limited to 255 characters
- The image descriptions will be limited to 1000 characters
- The links will be limited to 255 characters

A separate table will hold the chat history for each haiku and will have the following columns:
- id (primary key, autoincrement)
- haiku id
- role ("user", "chatbot")
- message limited to 1000 characters

MinIO will be used to store the images and audios.
The bucket name will be the haiku.
The folder name will be the haiku id.
The object name will be the type of the object (image or audio)
and the number of the object (1, 2, 3) eg. "image-1", "audio-2".
The minio instance will be available at http://localhost:9000 by default but also configurable via environment variables.

FastAPI will be used to serve the app with these endpoints:
- POST /chat/{id}: for the user to interact with the chatbot
- GET /chat/{id}/history: for the user to get the chat history
- GET /haiku: for the user to get all haiku ids, text, and status
- GET /haiku/{id}: for the user to get the haiku based on the haiku id
- DELETE /haiku/{id}: for the user to delete the haiku based on the haiku id. This also deletes the chat history, images, and audios.

Rate limiting
The user will only be able to have one haiku that's in progress at a time.
Once the haiku is complete, the user will be able to start a new one and will not be able to interact with the old one except to delete it.
