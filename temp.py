from flask import Flask, request, jsonify
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.sampling_params import SamplingParams
import asyncio

app = Flask(__name__)

# Initialize the async engine
engine_args = AsyncEngineArgs(model="meta-llama/Meta-Llama-3-8B-Instruct")
engine = AsyncLLMEngine.from_engine_args(engine_args)

async def generate_text(prompt):
    results_generator = engine.generate(prompt, SamplingParams(temperature=0.7, top_p=0.9))
    async for request_output in results_generator:
        return request_output.outputs[0].text

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    messages = data.get('messages', [])
    
    # Convert messages to prompt (simple conversion)
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    
    # Generate response
    response_text = asyncio.run(generate_text(prompt))
    
    return jsonify({
        "choices": [{
            "message": {
                "role": "assistant",
                "content": response_text
            }
        }]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
