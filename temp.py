from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.sampling_params import SamplingParams
from pydantic import BaseModel
import uvicorn
from typing import List, Optional, Dict, Any
import uuid
import time

app = FastAPI(title="vLLM LangChain Compatible API")

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

# Initialize engine
engine_args = AsyncEngineArgs(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    tensor_parallel_size=1
)
engine = AsyncLLMEngine.from_engine_args(engine_args)

def format_to_llama3_prompt(messages: List[Message]) -> str:
    """Convert messages to Llama 3 chat template format"""
    B_INST, E_INST = "<|start_header_id|>", "<|end_header_id|>"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    BOS, EOS = "<|begin_of_text|>", "<|eot_id|>"
    
    prompt = BOS
    for message in messages:
        if message.role == "system":
            prompt += f"{B_INST}system{E_INST}\n\n{B_SYS}{message.content}{E_SYS}"
        else:
            prompt += f"{B_INST}{message.role}{E_INST}\n\n{message.content}{EOS}"
    prompt += f"{B_INST}assistant{E_INST}\n\n"
    return prompt

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # Format prompt according to Llama 3's chat template
        prompt = format_to_llama3_prompt(request.messages)
        
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens
        )
        
        # Generate response
        request_id = str(uuid.uuid4())
        output = None
        async for request_output in engine.generate(prompt, sampling_params, request_id):
            output = request_output
        
        if not output:
            raise HTTPException(status_code=500, detail="No generation output")
        
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output.outputs[0].text,
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(output.prompt_token_ids),
                "completion_tokens": len(output.outputs[0].token_ids),
                "total_tokens": len(output.prompt_token_ids) + len(output.outputs[0].token_ids)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
