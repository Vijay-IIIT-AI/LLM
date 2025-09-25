docker build -t multi-model-gpu-api .

docker run --gpus all -p 8000:8000 multi-model-gpu-api


FROM pytorch/pytorch:2.7.1-cuda11.8-cudnn9-runtime
