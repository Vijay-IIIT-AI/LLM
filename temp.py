docker build -t multi-model-gpu-api .

docker run --gpus all -p 8000:8000 multi-model-gpu-api
