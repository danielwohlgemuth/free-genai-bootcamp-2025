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

5. Setup the storage:
```bash
python storage.py
```

6. Grant access to bedrock models:

Create inference profiles and copy the resulting ARN into the .env file.

```bash
aws bedrock create-inference-profile \
--inference-profile-name "amazon-titan-text-express-v1" \
--model-source copyFrom="arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1"

aws bedrock create-inference-profile \
--inference-profile-name "amazon-titan-image-generator-v1" \
--model-source copyFrom="arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-image-generator-v1"
```

7. Start the FastAPI server:
```bash
uvicorn main:app --port 8001 --reload
```

## Inspect the database

Connect to the database:
```bash
docker exec -it haiku-generator-backend-db-1 psql -U user haiku
```
