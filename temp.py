import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from vllm import AsyncLLMEngine, SamplingParams

app = FastAPI()
engine = None

# OpenAI-compatible request model
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 512
    stream: Optional[bool] = False

@app.on_event("startup")
async def startup_event():
    global engine
    engine = await AsyncLLMEngine.from_engine_args(
        model="unsloth/llama-3-8b-instruct",
        dtype="float16",
        tensor_parallel_size=2,
        gpu_memory_utilization=0.90,
        worker_use_ray=False,  # optional
        # Set CUDA_VISIBLE_DEVICES via env or do this:
        enforce_eager=True,  # VLLM sometimes needs this with certain configs
    )

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    global engine

    # Convert messages to prompt
    prompt = ""
    for m in request.messages:
        prompt += f"{m.role.capitalize()}: {m.content}\n"
    prompt += "Assistant:"

    sampling_params = SamplingParams(
        temperature=request.temperature or 0.0,
        max_tokens=request.max_tokens or 512,
        stop=["User:", "Assistant:"]
    )

    outputs = await engine.generate(prompt, sampling_params)
    output_text = outputs[0].outputs[0].text.strip()

    return JSONResponse(content={
        "id": "chatcmpl-001",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output_text
                },
                "finish_reason": "stop"
            }
        ],
        "model": request.model
    })

if __name__ == "__main__":
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = "3,4"
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
