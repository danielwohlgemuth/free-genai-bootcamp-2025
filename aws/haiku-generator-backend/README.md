# Haiku Generator Backend

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Start Ollama, MinIO, and PostgreSQL:

```bash
docker-compose up -d --build
```

4. Setup the database:
```bash
python database.py
```

5. Start the FastAPI server:
```bash
uvicorn main:app --port 8001 --reload
```
