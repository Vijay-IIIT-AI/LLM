@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    global engine

    # Build prompt
    prompt = ""
    for msg in request.messages:
        prompt += f"{msg.role.capitalize()}: {msg.content}\n"
    prompt += "Assistant:"

    sampling_params = SamplingParams(
        temperature=request.temperature or 0.0,
        max_tokens=request.max_tokens or 512,
        stop=["User:", "Assistant:"]
    )

    # Async generator from engine.generate
    outputs = engine.generate(
        prompt,
        sampling_params,
        request_id=str(uuid.uuid4())
    )

    # Get result from async generator
    async for output in outputs:
        response_text = output.outputs[0].text.strip()
        break

    return {
        "id": "chatcmpl-001",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": response_text},
            "finish_reason": "stop"
        }],
        "model": request.model
    }
