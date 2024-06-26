# Use the official Python image from the Docker Hub
# FROM python:3.9-slim
FROM ollama/ollama:latest

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

# Copy the necessary files and directories into the container
COPY parsing/ ./parsing/
COPY categorization/ ./categorization/
COPY full_annotation.py .
COPY entrypoint.sh .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
