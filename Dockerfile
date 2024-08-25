# Use the official Python image from the Docker Hub
# FROM python:3.9-slim
FROM ollama/ollama:latest

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

# Copy the necessary files and directories into the container
COPY ./app/ /app/
COPY ./entrypoint.sh ./

# Make port 8000 available to the world outside this container
EXPOSE 9000

# Define environment variable

ENV PORT=9000


# Make the entrypoint script executable
RUN chmod +x ./entrypoint.sh
RUN apt-get update && apt-get install -y curl

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
