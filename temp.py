# Use a Python base image
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install Python
RUN apt update && apt install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install vLLM
RUN pip install --no-cache-dir vllm

# Expose the API port
EXPOSE 8000

# Run vLLM server
CMD ["vllm", "serve", "microsoft/Florence-2-large", "--host", "0.0.0.0"]
