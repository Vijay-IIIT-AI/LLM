docker build -t multi-model-gpu-api .

docker run --gpus all -p 8000:8000 multi-model-gpu-api


FROM pytorch/pytorch:2.7.1-cuda11.8-cudnn9-runtime

entrypoint.sh

#!/bin/bash
# -------------------------
# Entrypoint for Docker container
# -------------------------

# Start FastAPI in background
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 &
APP_PID=$!

# Give the server some time to start
echo "Waiting for FastAPI to start..."
sleep 5

# Run the API test script
python test_api_multiple_models.py
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "❌ API tests failed. Stopping FastAPI..."
    kill $APP_PID
    exit 1
fi

echo "✅ API tests passed. FastAPI continues running..."
wait $APP_PID


FROM pytorch/pytorch:2.7.1-cuda11.8-cudnn9-runtime

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and scripts
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]



from fastapi import FastAPI
import torch

app = FastAPI(title="GPU Multi-Model API")

# Assume embedding_models and reranker_models are already loaded

@app.get("/health")
def health():
    # Check FastAPI is alive
    try:
        # Optional: quick test with a single dummy inference per model
        for name, model in embedding_models.items():
            _ = model.encode(["healthcheck"], convert_to_tensor=True)

        for name, model in reranker_models.items():
            dummy_input = torch.randn(1, model(torch.randn(1)).shape[0]).cuda()
            with torch.no_grad():
                _ = model(dummy_input)

        return {"status": "ok", "models": "all loaded"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

