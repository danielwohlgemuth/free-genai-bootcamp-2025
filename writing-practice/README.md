# Kana Writing Practice

An interactive web application for practicing Japanese kana writing using AWS services and Gradio interface.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure AWS credentials:
   - Create a `.env` file in the project root with:
     ```
     AWS_ACCESS_KEY_ID=your_access_key
     AWS_SECRET_ACCESS_KEY=your_secret_key
     AWS_REGION=your_region
     ```

## Running the Application

1. Start the application:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:7860`

## Usage

1. Select a kana group from the dropdown menu
2. Draw the displayed kana character in the canvas
3. Click Submit to check your writing
4. Practice and improve!

## Docker Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with your AWS credentials and settings
3. Build and run with Docker Compose:
   ```bash
   docker compose up --build
   ```
4. Access the application at `http://localhost:7860`

## Features
- Interactive writing canvas with real-time feedback
- Multiple kana groups for comprehensive practice
- AI-powered character recognition using AWS SageMaker
- Practice history tracking and statistics
- Rate limiting and error handling for reliability
- Docker support for easy deployment
- AWS Bedrock integration for word generation and translation
- Amazon Polly integration for audio playback
- Progress tracking and performance metrics

## Technical Uncertainty
- Will AWS Bedrock even work? It didn't work in a previous attempt. See https://github.com/danielwohlgemuth/ai-recipe-generator.
- Is Amazon Developer Q usable enough to generate the code for the app?
    - Generating the tech specs with Developer Q produced reasonable results, but it took a long time to generate its output and it created new files instead of updating the existing one.
    - Generating the code didn't go as expected. It was supposed to use AWS Bedrock, Amazon Polly, backend API, Manga OCR, and it didn't do any of them. Instead, it created a json file instead of using the backend API, it integrated with Amazon SageMaker to recognize characters instead of using Manga OCR, and it made use of Amazon DynamoDB to store results when it was specified not to do that.
    - The things that Developer Q did well is generating tests, a setup script, and Docker files to go along the project.

## Setup
1. Install dependencies
2. Configure AWS credentials
3. Run the Gradio application

## Development
See [Technical Specs](Technical-Specs.md) for detailed architecture and implementation plans.
