# Use Ubuntu as base
FROM ubuntu:22.04

# Avoid tzdata interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/download/OllamaLinuxInstaller.sh | sh

# Expose Ollama’s API port
EXPOSE 8081

# Pull the model (replace gpt-oss with your desired model name)
RUN ollama pull gpt-oss

# Start Ollama serving on port 8081
CMD ["ollama", "serve", "--port", "8081"]
