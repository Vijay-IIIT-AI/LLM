from openai import OpenAI

client = OpenAI(
    api_key="YOUR_CUSTOM_API_KEY",
    base_url="https://your-llm-server.com/v1"
)

response = client.chat.completions.create(
    model="your-custom-model",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about the ocean."}
    ]
)

print(response.choices[0].message.content)
