#!/bin/bash

# Build the application image
echo "Building application image..."
docker compose build app

# Start all services
echo "Starting all services..."
docker compose up -d

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 10

# Pull required models
echo "Pulling required models..."
docker compose exec ollama ollama pull bge-m3
docker compose exec ollama ollama pull llama2:1b

echo "Setup complete! Application is running at http://localhost:8000"
