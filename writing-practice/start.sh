#!/bin/bash

# Start the FastAPI backend
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Start the Gradio frontend
python app.py
