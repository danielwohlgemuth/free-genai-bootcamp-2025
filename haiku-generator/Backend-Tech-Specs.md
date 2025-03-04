# Haiku Generator

Generate haikus based on a topic provided by the user.

## Business Goal

provide a chatbot with which the user can interact. the chatbot will help the user pick a topic, and the chatbot will generate a haiku based on that topic in English. if the user agrees with the haiku, the chatbot will generate three images and audios, each corresponding to one line of the haiku. if the user disagrees, the chatbot will help the user refine the topic. the chatbot will have access to a tool that will generate the images and audios. The chatbot will translate the haiku into Japanese and the generated audio will be based on the Japanese version of the haiku.

## Architecture

The app will consist of an agentic workflow with two tools available: one to kick off the generation of the images and audios, and another to check if the generation has completed.

The tool to kick off the generation of the images and audios will be a function that takes the haiku as input and returns the haiku id.
For each line of the haiku, the tool will translate the line into Japanese and generate the audio based on the Japanese version of the line. It will also generate the image description and then generate the image based on the image description. To ensure consistency between the images, the description of the first image will flow into the generation of the image description for the second image, and the description of the first and second image will flow into the generation of the image description for the third image.

The tool to check if the generation has completed will be a function that takes the haiku id as input and returns a response saying that it has completed, there was an error, or it is still in progress.

## Technical Specs

Use the OPEA (Open Platform for Enterprise AI) framework.

Images will be generated using https://huggingface.co/stabilityai/stable-diffusion-3.5-medium, with num_inference_steps=5.

Audios will be generated using the coqui-tts package, with the tts_models/multilingual/multi-dataset/xtts_v2 model, the language set to Japanese, and the speaker set to Chandra MacFarland.

The translation from English to Japanese will be done using https://huggingface.co/Qwen/Qwen2-7B

SQLite will be used to store information about the haiku and each row will include the following information:
- haiku id
- status ("in progress", "completed", "failed")
- error message (if any)
- haiku line 1
- haiku line 2
- haiku line 3
- image description 1
- image description 2
- image description 3
- image link 1
- image link 2
- image link 3
- audio link 1
- audio link 2
- audio link 3

MinIO will be used to store the images and audios. The bucket name will be the haiku id.

FastAPI will be used to serve the app with these endpoints:
- /chat: for the user to interact with the chatbot
- /haiku: for the user to get all haiku ids
- /haiku/{id}: for the user to get the haiku based on the haiku id
