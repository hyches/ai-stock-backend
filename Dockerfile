# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev libssl-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 