# Haiku Generator

Generate haikus based on a topic provided by the user.

## Business Goal

provide a chatbot with which the user can interact. the chatbot will help the user pick a topic, and the chatbot will generate a haiku based on that topic in English. if the user agrees with the haiku, the chatbot will generate three images and audios, each corresponding to one line of the haiku. if the user disagrees, the chatbot will help the user refine the topic. the chatbot will have access to a tool that will generate the images and audios. The chatbot will translate the haiku into Japanese and the generated audio will be based on the Japanese version of the haiku.

Images will be generated using https://huggingface.co/stabilityai/stable-diffusion-3.5-medium, with num_inference_steps=5.

Audios will be generated using the coqui-tts package, with the tts_models/multilingual/multi-dataset/xtts_v2 model, the language set to Japanese, and the speaker set to Chandra MacFarland.

The translation from English to Japanese will be done using https://huggingface.co/Qwen/Qwen2-7B
