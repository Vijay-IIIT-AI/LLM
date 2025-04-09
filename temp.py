import requests

url = "http://localhost:8000/v1/chat/completions"

payload = {
    "model": "unsloth/llama-3-8b-instruct",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    "temperature": 0.0,
    "max_tokens": 64,
    "stream": False
}

response = requests.post(url, json=payload)

print("Status Code:", response.status_code)
print("Response JSON:")
print(response.json())
