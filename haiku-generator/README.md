# Haiku Generator

This project provides a chatbot for user interaction to generate haikus and a corresponding image and audio for each line of the haiku.

## What is a Haiku?

A haiku is a traditional Japanese poem with the following format:
- Three lines
- Syllable pattern:
    - 5 syllables in the first line
    - 7 syllables in the second line
    - 5 syllables in the third line

Example:
```text
Silent autumn breeze
Golden leaves drift to the ground
Whispers of the past
```

## Backend

[Backend Tech Specs](Backend-Tech-Specs.md)

### Agentic Workflow

An agentic workflow is a chatbot with which users can interact and where the chatbot can decide to use the tools available to it, in this case, to save the haiku and start generating the media content.

![Agentic Workflow](assets/agentic-workflow.drawio.png)

[Agentic Workflow file](https://app.diagrams.net/?title=agentic-workflow#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fdanielwohlgemuth%2Ffree-genai-bootcamp-2025%2Frefs%2Fheads%2Fmain%2Fhaiku-generator%2Fassets%2Fagentic-workflow.drawio)

### Media Generation Workflow

The media generation workflow has two parts: generate an image and an audio for each line of the haiku.

Generating the image can be broken down into two steps: generate an image description and generate the image. The image description is generated sequentially with the intention to make the descriptions be consistent, while the image is generated in parallel.

Generating the audio can also be broken down into two steps: generate a translation and generate the audio, both in parallel since there is no dependency between each line.

![Media Workflow](assets/media-mermaid.png)

[Media Workflow file](assets/media.mermaid)

### Backend API

![Backend API](assets/backend-api.png)

### Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Setup the database:
```bash
python database.py
```

4. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

### Usage

```bash
docker-compose up -d --build
```
