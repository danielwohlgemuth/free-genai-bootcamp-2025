from langchain import LLMChain, PromptTemplate
from langchain.llms import Ollama
import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, filename='haiku_generator.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Ollama model
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
ollama_model = Ollama(model=MODEL_NAME)

# Function to retrieve chat history for a specific haiku_id

def retrieve_chat_history(haiku_id: str):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    history = cursor.fetchall()
    conn.close()
    return history

# Function to store user interaction in chat history

def store_chat_interaction(haiku_id: str, user_message: str, response: str):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (haiku_id, user_message, response)
        VALUES (?, ?, ?)
    ''', (haiku_id, user_message, response))
    conn.commit()
    conn.close()

# Function to generate haiku
async def generate_haiku(user_message: str, haiku_id: str):
    try:
        # Retrieve chat history for the haiku_id
        chat_history = retrieve_chat_history(haiku_id)

        # Create prompt based on user message and chat history
        prompt = create_prompt(user_message, chat_history)

        # Generate haiku
        haiku = await ollama_model.generate(prompt)
        logging.info(f"Haiku generated: {haiku}")

        # Store the interaction in chat history
        store_chat_interaction(haiku_id, user_message, haiku)

        # Return generated haiku
        return haiku
    except Exception as e:
        logging.error(f"Error generating haiku: {e}")
        raise

# Function to handle user feedback and refine haiku
async def handle_user_feedback(haiku_id: str, user_feedback: str):
    # Logic to refine the haiku based on user feedback
    if user_feedback.lower() == 'satisfied':
        # Proceed to generate multimedia
        multimedia = await generate_multimedia(haiku_id)
        return multimedia
    else:
        # Logic to refine the haiku based on feedback
        refined_haiku = await refine_haiku(haiku_id, user_feedback)
        return refined_haiku

# Function to refine haiku
async def refine_haiku(haiku_id: str, user_feedback: str):
    # Logic to refine the haiku based on user feedback
    pass

# Function to generate multimedia (images and audio)
async def generate_multimedia(haiku_id: str):
    # Logic to generate images and audio for the haiku
    image = await generate_image(haiku_id)
    audio = await generate_audio(haiku_id)
    haiku = await retrieve_haiku(haiku_id)
    translation = await translate_haiku(haiku)
    return {'image': image, 'audio': audio, 'translation': translation}

# Function to create image description based on haiku
async def create_image_description(haiku: str):
    return f'An artistic representation of the haiku: {haiku}'

# Function to generate image
async def generate_image(haiku_id: str):
    # Retrieve the haiku from chat history
    haiku = await retrieve_haiku(haiku_id)

    # Create a description based on the haiku
    description = await create_image_description(haiku)

    # Call the image generation method from media_generation.py
    image_url = await generate_image_from_description(description)
    return image_url

# Function to generate audio
async def generate_audio(haiku_id: str):
    # Retrieve the haiku from chat history
    haiku = await retrieve_haiku(haiku_id)

    # Translate the haiku into Japanese
    translated_haiku = await translate_haiku(haiku)

    # Call the audio generation method from media_generation.py
    audio_url = await generate_audio_from_text(translated_haiku)
    return audio_url

# Function to translate haiku into Japanese
async def translate_haiku(haiku: str):
    try:
        # Create prompt for translation
        prompt = f'Translate the following haiku into Japanese: {haiku}'

        # Generate translation using Ollama model
        translation = await ollama_model.generate(prompt)
        logging.info(f"Haiku translated: {translation}")

        return translation
    except Exception as e:
        logging.error(f"Error translating haiku: {e}")
        raise

# Function to retrieve haiku from chat history
async def retrieve_haiku(haiku_id: str):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT response FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    haiku = cursor.fetchone()[0]
    conn.close()
    return haiku

# Function to create prompt based on user message and chat history

def create_prompt(user_message: str, chat_history: list):
    # Start with the user message
    prompt = f'User: {user_message}\n'

    # Add previous chat history to the prompt
    for entry in chat_history:
        user_msg, response = entry
        prompt += f'User: {user_msg}\nBot: {response}\n'

    # Add instruction for haiku generation
    prompt += 'Generate a haiku based on the above conversation.'

    return prompt
