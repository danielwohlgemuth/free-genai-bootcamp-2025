# Vocabulary Service

A service that generates Japanese vocabulary words based on topics using LLM.

## Setup

### Prerequisites
- Python 3.8+
- Docker
- Ollama

### Local Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install the requirements:
```bash
pip install -r requirements.txt
```

4. Run Ollama (if not already running):
```bash
ollama serve
```

5. Pull the LLM model:
```bash
ollama pull llama3.2:1b
```

6. Start the service:
```bash
python app.py
```

The service will be available at `http://localhost:8888/`

### Docker Setup

1. Build the image:
```bash
docker build -t vocab-service .
```

2. Run with Docker:
```bash
docker run -p 8888:8888 \
  -e OLLAMA_HOST=localhost \
  -e OLLAMA_PORT=11434 \
  -e OLLAMA_MODEL=llama3.2:1b \
  vocab-service
```

### Docker Compose Setup

Start the services:
```bash
docker compose up -d
```

## Usage

Send a POST request to `/`:

```bash
curl -X POST http://localhost:8888/ \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "food",
    "word_count": 5
  }'
```

### Environment Variables

- `MEGA_SERVICE_PORT`: Port for the service (default: 8888)
- `OLLAMA_HOST`: Ollama API endpoint (default: localhost)
- `OLLAMA_PORT`: Ollama API port (default: 11434)
- `OLLAMA_MODEL`: Ollama model to use (default: llama3.2:1b)

## Response Format

```json
{
    "group_name": "food",
    "words": [
        {
            "japanese": "寿司",
            "romaji": "sushi",
            "english": "sushi",
            "parts": {
                "type": "noun",
                "formality": "neutral"
            }
        }
        // ... more words
    ]
}
```


```bash
python app.py
```