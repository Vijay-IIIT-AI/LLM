import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_load_model():
    """Tests the /load_model endpoint."""
    response = requests.post(f"{BASE_URL}/load_model", json={"model_path": "TheBloke/LLaVA-1.5-7B-GGUF"})
    print("Load Model Response:", response.status_code, response.json())

def test_prompt_vision():
    """Tests the /prompt_vision endpoint."""
    test_payload = {
        "question": "What is in the image?",
        "image_paths": ["path/to/image1.png", "path/to/image2.jpg"]
    }
    
    response = requests.post(f"{BASE_URL}/prompt_vision", json=test_payload)
    print("Prompt Vision Response:", response.status_code, response.json())

if __name__ == "__main__":
    print("Testing API Endpoints...\n")
    
    # Test Load Model
    test_load_model()
    
    # Wait for the model to load before testing prompt (adjust sleep time if needed)
    import time
    time.sleep(5)  
    
    # Test Vision Prompt
    test_prompt_vision()
