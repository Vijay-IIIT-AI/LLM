FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Install Python and system dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip git curl && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --upgrade pip

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy your pre-downloaded model into the image
COPY Models /models/llama-3-8b

# Expose the server port
EXPOSE 8000

# Run the OpenAI-compatible API server with your local model
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "/models/llama-3-8b", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
