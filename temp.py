curl -X POST http://localhost:8000/v1/completions \
     -H "Content-Type: application/json" \
     -d '{
           "model": "/models",
           "prompt": "What is the capital of France?",
           "max_tokens": 50,
           "temperature": 0,
           "top_k": 1
         }'
