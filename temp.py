from fastapi import FastAPI
from pydantic import BaseModel
from vllm import LLM, SamplingParams
import uvicorn

app = FastAPI()
llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 256

def format_prompt(messages):
    prompt = ""
    for m in messages:
        prompt += f"{m.role}: {m.content}\n"
    prompt += "assistant: "
    return prompt

@app.post("/v1/chat/completions")
async def chat_completion(req: ChatRequest):
    prompt = format_prompt(req.messages)
    sampling_params = SamplingParams(
        temperature=req.temperature,
        top_p=req.top_p,
        max_tokens=req.max_tokens,
    )
    outputs = llm.generate(prompt, sampling_params)
    if not outputs or not outputs[0].outputs:
        return {
            "id": "chatcmpl-xyz",
            "object": "chat.completion",
            "choices": [],
            "error": "no generation chunks were returned"
        }

    output_text = outputs[0].outputs[0].text.strip()

    return {
        "id": "chatcmpl-xyz",
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
        "model": req.model
    }
