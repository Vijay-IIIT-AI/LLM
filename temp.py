import os
import requests
from time import sleep

api_key = "mjLoMvjl6nnvofomLxPNDMWZsvuouvCz"

def translate(text: str, tgt: str = "Korean") -> str:
    sleep(10)
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": f"You are a professional Korean translator to {tgt}.Just translate what is there don't give any extra information your just translator"},
            {"role": "user", "content": text}
        ]
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# Test
print(translate("Hello, how are you?", "Korean"))
