FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=7860
ENV HOST=0.0.0.0

# Expose the port
EXPOSE $PORT

# Run the application
CMD ["python", "app.py"]