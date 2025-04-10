from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.sampling_params import SamplingParams
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any
import uuid
import time

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
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 512

engine = AsyncLLMEngine.from_engine_args(
    AsyncEngineArgs(model="meta-llama/Meta-Llama-3-8B-Instruct")
)

def format_llama3_prompt(messages: List[Message]) -> str:
    prompt = ""
    for msg in messages:
        if msg.role == "system":
            prompt += f"<|start_header_id|>system<|end_header_id|>\n\n{msg.content}<|eot_id|>"
        else:
            prompt += f"<|start_header_id|>{msg.role}<|end_header_id|>\n\n{msg.content}<|eot_id|>"
    prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
    return prompt

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        prompt = format_llama3_prompt(request.messages)
        
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens
        )
        
        request_id = str(uuid.uuid4())
        final_output = None
        
        async for request_output in engine.generate(
            prompt=prompt,
            sampling_params=sampling_params,
            request_id=request_id
        ):
            final_output = request_output
        
        if not final_output:
            raise HTTPException(status_code=500, detail="No output generated")
        
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": final_output.outputs[0].text,
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(final_output.prompt_token_ids),
                "completion_tokens": len(final_output.outputs[0].token_ids),
                "total_tokens": len(final_output.prompt_token_ids) + len(final_output.outputs[0].token_ids)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
