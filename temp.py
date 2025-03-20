import asyncio
import base64
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs

app = FastAPI()

# Global model engine
vision_model_engine = None

class VisionPromptRequest(BaseModel):
    question: str
    image_paths: list[str]

# Function to encode images to base64
def encode_image(image_path):
    """Encodes an image to base64 format."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to process images into vLLM format
def process_images(image_paths):
    """Processes multiple image paths into vLLM-compatible format."""
    return [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(img_path)}"}}
        for img_path in image_paths
    ]

@app.post("/load_model")
async def load_model(model_path: str = "TheBloke/LLaVA-1.5-7B-GGUF"):
    """Loads the vision model globally."""
    global vision_model_engine
    if vision_model_engine is not None:
        return {"message": "Model already loaded"}
    
    try:
        engine_args = AsyncEngineArgs(
            model=model_path,
            max_model_len=4096,
            max_num_seqs=16
        )
        vision_model_engine = AsyncLLMEngine.from_engine_args(engine_args)
        return {"message": "Model loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")

@app.post("/prompt_vision")
async def prompt_vision(request: VisionPromptRequest):
    """Processes vision prompt with text and images."""
    global vision_model_engine
    if vision_model_engine is None:
        raise HTTPException(status_code=400, detail="Model not loaded. Call /load_model first.")

    try:
        # Convert images to required format
        image_content = process_images(request.image_paths)

        # Prepare the input payload
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": request.question},
                *image_content
            ],
        }]

        # Run async inference
        async for output in vision_model_engine.chat(messages):
            return {"response": output}
    
    except FileNotFoundError as fnf_error:
        raise HTTPException(status_code=400, detail=str(fnf_error))
    except ValueError as value_error:
        raise HTTPException(status_code=400, detail=str(value_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

