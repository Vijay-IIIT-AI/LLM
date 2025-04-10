from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.sampling_params import SamplingParams
from pydantic import BaseModel
import uvicorn
from typing import List, Optional, Dict, Any
import uuid
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = 512

engine_args = AsyncEngineArgs(model="meta-llama/Meta-Llama-3-8B-Instruct")
engine = AsyncLLMEngine.from_engine_args(engine_args)

async def generate_text(prompt: str, sampling_params: SamplingParams) -> str:
    request_id = str(uuid.uuid4())
    results_generator = engine.generate(prompt, sampling_params, request_id)
    async for request_output in results_generator:
        return request_output.outputs[0].text
    return ""

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest) -> Dict[str, Any]:
    try:
        # Format prompt according to Llama 3's chat template
        prompt = "<|begin_of_text|>"
        for msg in request.messages:
            prompt += f"<|start_header_id|>{msg.role}<|end_header_id|>\n\n{msg.content}<|eot_id|>"
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens
        )
        
        response_text = await generate_text(prompt, sampling_params)
        
        return {
            "id": f"chatcmpl-{str(uuid.uuid4())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text,
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,  # You can implement token counting
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
