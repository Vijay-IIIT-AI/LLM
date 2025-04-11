CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "/models/llama-3-8b", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--dtype", "float16"]
