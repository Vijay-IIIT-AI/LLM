import asyncio
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vllm import AsyncLLMEngine, SamplingParams, EngineArgs

# Initialize FastAPI
app = FastAPI()

# Global model instance
model = None  

# Model config
MODEL_NAME = "meta-llama/Llama-3.2-11B-Vision-Instruct"

class VisionPromptRequest(BaseModel):
    question: str
    image_paths: list[str]  # Local image paths

def encode_image(image_path: str) -> str:
    """Encodes an image as base64 for vLLM processing."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading image {image_path}: {str(e)}")

@app.post("/load_model")
async def load_model():
    """Loads the vision model globally."""
    global model
    if model is None:
        try:
            engine_args = EngineArgs(
                model=MODEL_NAME,
                max_model_len=4096,
                max_num_seqs=16,
                limit_mm_per_prompt={"image": 2}  # Adjust for number of images
            )
            model = AsyncLLMEngine.from_engine_args(engine_args)
            await model.initialize()
            return {"message": "Model loaded successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")
    return {"message": "Model already loaded"}

@app.post("/prompt_vision")
async def prompt_vision(request: VisionPromptRequest):
    """Processes vision input using the loaded model."""
    global model
    if model is None:
        raise HTTPException(status_code=400, detail="Model not loaded. Call /load_model first.")

    try:
        # Encode images
        image_data = [encode_image(path) for path in request.image_paths]

        # Prepare prompt with placeholders
        placeholders = "<|image|>" * len(image_data)
        prompt = f"{placeholders}<|begin_of_text|>{request.question}"

        # Define Sampling Parameters
        sampling_params = SamplingParams(temperature=0.7, max_tokens=512)

        # Generate response asynchronously
        output = await model.async_generate(prompt, sampling_params, image_data=image_data)

        return {"response": output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during inference: {str(e)}")

# Run model loading asynchronously on startup
@app.on_event("startup")
async def startup_event():
    await load_model()
