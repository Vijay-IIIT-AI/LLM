from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.sampling_params import SamplingParams
from pydantic import BaseModel
import uvicorn
from typing import List, Optional

app = FastAPI()

# Add CORS middleware to allow requests from your frontend or other services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = 512

# Initialize the async engine
engine_args = AsyncEngineArgs(model="meta-llama/Meta-Llama-3-8B-Instruct")
engine = AsyncLLMEngine.from_engine_args(engine_args)

async def generate_text(prompt: str, sampling_params: SamplingParams):
    results_generator = engine.generate(prompt, sampling_params)
    async for request_output in results_generator:
        return request_output.outputs[0].text

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # Convert messages to prompt (adjust this based on your model's requirements)
        prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
        
        # Create sampling params from request
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens
        )
        
        # Generate response
        response_text = await generate_text(prompt, sampling_params)
        
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response_text
                }
            }]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
