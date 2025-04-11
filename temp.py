FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Install Python & dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip git curl && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --upgrade pip

# Install vLLM and optional dependencies
RUN pip install vllm[all] accelerate transformers

# Download model at build time (optional but faster if baked in)
RUN mkdir -p /models && \
    python -c "from huggingface_hub import snapshot_download; \
               snapshot_download(repo_id='unsloth/llama-3-8b-Instruct', local_dir='/models/llama-3-8b', local_dir_use_symlinks=False)"

# Expose port
EXPOSE 8000

# Default command to run OpenAI-compatible vLLM server
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "/models/llama-3-8b", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
