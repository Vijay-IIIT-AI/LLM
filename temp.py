def format_prompt(messages):
    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"<|system|>\n{msg['content']}\n"
        elif msg["role"] == "user":
            prompt += f"<|user|>\n{msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"<|assistant|>\n{msg['content']}\n"
    prompt += "<|assistant|>\n"
    return prompt


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    prompt = format_prompt([msg.dict() for msg in request.messages])

    sampling_params = SamplingParams(
        temperature=0.0,
        max_tokens=512,
        stop=["<|user|>", "<|system|>", "<|assistant|>"]
    )

    outputs = engine.generate(
        prompt,
        sampling_params,
        request_id=str(uuid.uuid4())
    )

    async for output in outputs:
        print("== Raw output:", output)
        response_text = output.outputs[0].text.strip()
        break

    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": response_text
            }
        }]
    }
