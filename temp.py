# run_api.py

from fastapi import FastAPI
from pydantic import BaseModel
from vllm import LLM, SamplingParams
import uvicorn
import threading

# Initialize FastAPI
app = FastAPI()

# Load vLLM model
llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct")

# Request/Response structure
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 256

# Prompt formatter
def format_prompt(messages):
    prompt = "<|begin_of_text|>"
    for msg in messages:
        prompt += f"<|start_header_id|>{msg.role}<|end_header_id|>\n{msg.content}<|eot_id|>"
    prompt += "<|start_header_id|>assistant<|end_header_id|>"
    return prompt

# Route
@app.post("/v1/chat/completions")
async def chat_completion(request: ChatRequest):
    prompt = format_prompt(request.messages)
    sampling_params = SamplingParams(
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens,
    )
    outputs = llm.generate(prompt, sampling_params)
    result = outputs[0].outputs[0].text
    return {
        "id": "chatcmpl-001",
        "object": "chat.completion",
        "choices": [{"message": {"role": "assistant", "content": result}}],
    }

# Auto-run server from script
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
