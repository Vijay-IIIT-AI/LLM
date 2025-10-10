import aiohttp

async def get_image_from_pexels(self, prompt: str) -> str:
    """
    Modified to call your Stable Diffusion API instead of Pexels.
    Keeps the same function name and return type (image_url as str).
    """
    async with aiohttp.ClientSession(trust_env=True) as session:
        # Call your local Stable Diffusion API
        response = await session.post(
            "http://127.0.0.1:8000/generate",  # 👈 change this if deployed
            json={"prompt": prompt},
            timeout=aiohttp.ClientTimeout(total=300),  # allow long generation time
        )

        if response.status != 200:
            text = await response.text()
            raise RuntimeError(f"Image generation failed ({response.status}): {text}")

        data = await response.json()
        image_url = data.get("url")

        if not image_url:
            raise ValueError("No image URL returned from Stable Diffusion API")

        return image_url


--------------------------------
"""
FastAPI + diffusers example:
POST /generate  -> { "prompt": "A fantasy castle" }  => returns {"url": ".../images/<uuid>.png"}
Serves images at /images/<filename>

Requirements:
pip install fastapi uvicorn diffusers transformers accelerate safetensors pillow python-multipart
Install torch separately appropriate to your CUDA version (or CPU-only)
"""
import os
import uuid
import asyncio
from io import BytesIO
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import torch
from PIL import Image
from diffusers import StableDiffusionPipeline

# -------------------------
# Config
# -------------------------
MODEL_ID = "runwayml/stable-diffusion-v1-5"  # change if you want another HF model
IMAGES_DIR = Path("./images")
IMAGES_DIR.mkdir(exist_ok=True)
MAX_PROMPT_LENGTH = 1000

# -------------------------
# Load model (once)
# -------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Starting — device = {device}. Loading model {MODEL_ID} ...")

# set torch_dtype to float16 if GPU available to save memory
torch_dtype = torch.float16 if device == "cuda" else torch.float32

# Loading can take a while and lots of RAM/VRAM
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=torch_dtype,
    safety_checker=None,  # optional: include or handle safety check separately
    revision="fp16" if device == "cuda" else None,
)
pipe = pipe.to(device)
pipe.enable_attention_slicing()  # reduce VRAM peak

# optional: reduce memory by disabling text encoder gradients etc.
# -------------------------
# App + concurrency guard
# -------------------------
app = FastAPI(title="Stable Diffusion API")

# allow CORS from anywhere for demo (in prod, lock down allowed origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount images directory so generated images are accessible via URL
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

generation_lock = asyncio.Lock()  # prevent multiple inferences at exactly same time (optional)

# -------------------------
# Request model
# -------------------------
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt to generate image from")
    width: Optional[int] = Field(512, ge=64, le=1024)
    height: Optional[int] = Field(512, ge=64, le=1024)
    num_inference_steps: Optional[int] = Field(20, ge=1, le=150)
    guidance_scale: Optional[float] = Field(7.5, ge=1.0, le=20.0)
    seed: Optional[int] = Field(None, description="Optional random seed for deterministic output")

# -------------------------
# Helpers
# -------------------------
def _save_pil_image(image: Image.Image, out_path: Path):
    image.save(out_path, format="PNG", optimize=True)

async def run_generation(prompt: str, width: int, height: int, steps: int, guidance: float, seed: Optional[int]):
    # Run CPU-bound or blocking model call off the event loop
    def _sync_infer():
        generator = torch.Generator(device=device)
        if seed is not None:
            generator = generator.manual_seed(seed)
        # supply width/height to the pipeline if supported (some pipelines accept these args)
        result = pipe(
            prompt,
            height=height,
            width=width,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator if seed is not None else None,
        )
        # result.images is a list of PIL images
        return result.images[0]

    img = await asyncio.to_thread(_sync_infer)
    return img

# -------------------------
# Endpoints
# -------------------------
@app.post("/generate")
async def generate(req: GenerateRequest, request: Request):
    # Basic validation
    if not req.prompt or len(req.prompt.strip()) == 0:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    if len(req.prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Prompt too long (max {MAX_PROMPT_LENGTH} chars).")

    # Acquire a lock so only one generation runs at a time (optional but safer on limited GPUs)
    async with generation_lock:
        try:
            pil_img = await run_generation(
                prompt=req.prompt,
                width=req.width,
                height=req.height,
                steps=req.num_inference_steps,
                guidance=req.guidance_scale,
                seed=req.seed,
            )
        except Exception as e:
            # give helpful error to user
            raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    # Save image with uuid filename
    fname = f"{uuid.uuid4().hex}.png"
    out_path = IMAGES_DIR / fname
    _save_pil_image(pil_img, out_path)

    # Build URL to image using request.base_url
    base = str(request.base_url).rstrip("/")  # e.g. http://127.0.0.1:8000
    url = f"{base}/images/{fname}"

    return {"url": url, "filename": fname}

@app.get("/health")
async def health():
    return {"status": "ok", "device": device, "model": MODEL_ID}


---

python -m venv venv
source venv/bin/activate
# Install torch separately for GPU or CPU as recommended by pytorch.org.
# Example CPU-only:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Then:
pip install fastapi uvicorn diffusers transformers accelerate safetensors pillow



-----

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
