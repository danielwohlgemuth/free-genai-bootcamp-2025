# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables
ENV BACKEND_SERVICE_URL=http://backend:8888

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"] 