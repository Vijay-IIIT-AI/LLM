from unsloth import FastVisionModel
from transformers import TextStreamer
import torch
from PIL import Image

#LLAMA Model - "unsloth/Llama-3.2-11B-Vision-Instruct"
#Pixtral Model - ""unsloth/Pixtral-12B-Base-2409-bnb-4bit""
# Load the model in 16-bit
model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Llama-3.2-11B-Vision-Instruct",
    load_in_4bit=False,  # Use full precision (16-bit)   
    device_map="auto"
)

# Enable inference mode
FastVisionModel.for_inference(model)
