# Kana Writing Practice

An interactive web application for practicing Japanese kana writing using AWS services and Gradio interface.

## Technical Uncertainty
- Will AWS Bedrock even work? It didn't work in a previous attempt. See https://github.com/danielwohlgemuth/ai-recipe-generator.
- Is Amazon Developer Q usable enough to generate the code for the app?
    - Generating the tech specs with Developer Q produced reasonable results, but it took a long time to generate its output and it created new files instead of updating the existing one.
    - Generating the code didn't go as expected. It was supposed to use AWS Bedrock, Amazon Polly, backend API, Manga OCR, and it didn't do any of them. Instead, it created a json file instead of using the backend API, it integrated with Amazon SageMaker to recognize characters instead of using Manga OCR, and it made use of Amazon DynamoDB to store results when it was specified not to do that.
    - The things that Developer Q did well is generating tests, a setup script, and Docker files to go along the project.

## Features
- Interactive drawing canvas (300px high, 900px wide)
- Word group selection interface (Hiragana and Katakana)
- Clear canvas functionality
- AWS Bedrock integration for kana representation generation
- Amazon Polly integration for Japanese word audio synthesis
- Manga OCR for character recognition
- FastAPI backend for word and group management
- Caching system for frequently used words and audio

## Prerequisites
- Python 3.9+
- AWS Account with access to:
  - AWS Bedrock
  - Amazon Polly
- Docker and Docker Compose (optional)

## Local Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure AWS credentials:
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=your_region
   BACKEND_URL=http://localhost:8000
   ```

## Running the Application

### Method 1: Direct Python Execution

1. Start the FastAPI backend:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```

2. In a new terminal, start the Gradio frontend:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to:
   - Frontend: http://localhost:7860
   - API Documentation: http://localhost:8000/docs

### Method 2: Docker Compose

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` with your AWS credentials

3. Build and run with Docker Compose:
   ```bash
   docker compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:7860
   - API Documentation: http://localhost:8000/docs

## Usage

1. Select a kana group (Hiragana or Katakana) from the dropdown menu
2. The application will display:
   - English word
   - Kana representation
   - Audio pronunciation (click to play)
3. Draw the kana character in the canvas
4. Click "Submit" to check your writing
5. Use "Clear Canvas" to start over
6. Click "Next Word" to practice a different character

## Project Structure
```
writing-practice/
├── app.py          # Gradio frontend application
├── api.py          # FastAPI backend service
├── data/           # JSON files for words and groups
├── Dockerfile      # Docker container definition
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Python dependencies
├── start.sh           # Service startup script
└── .env              # Environment configuration
```

## Development
See [Technical Specs](Technical-Specs.md) for detailed architecture and implementation details.

## Error Handling
- The application includes comprehensive error handling for:
  - AWS service failures
  - Network connectivity issues
  - Invalid user input
  - Backend service unavailability

## Caching
- Audio files and kana representations are cached for improved performance
- The cache is memory-based and cleared when the application restarts
