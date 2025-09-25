from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import torch
from sentence_transformers import SentenceTransformer

app = FastAPI(title="GPU Multi-Model API")

# -------------------------
# Load Embedding Models ON GPU
# -------------------------
embedding_model_names = [
    "embedding_model_1",
    "embedding_model_2",
    # Add more models as needed
]
embedding_models = {}
for name in embedding_model_names:
    print(f"Loading {name} on GPU...")
    embedding_models[name] = SentenceTransformer(f"models/{name}", device="cuda")
print("All embedding models loaded.")

# -------------------------
# Load Reranker Models ON GPU
# -------------------------
reranker_model_names = [
    "reranker_model_1",
    "reranker_model_2",
    # Add more models as needed
]
reranker_models = {}
for name in reranker_model_names:
    model = torch.load(f"models/{name}.pt", map_location="cuda")
    model.eval()
    reranker_models[name] = model
print("All reranker models loaded.")

# -------------------------
# Request Schemas
# -------------------------
class EmbeddingRequest(BaseModel):
    model_name: str
    texts: List[str]  # Can be a single text or batch

class RerankerRequest(BaseModel):
    model_name: str
    query: str
    candidates: List[str]

# -------------------------
# Embedding Endpoint
# -------------------------
@app.post("/embed")
def embed(request: EmbeddingRequest):
    model = embedding_models.get(request.model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Embedding model not found")
    # Batch encode for efficiency
    embeddings = model.encode(request.texts, convert_to_tensor=True)
    return {"embeddings": embeddings.cpu().tolist()}

# -------------------------
# Reranker Endpoint
# -------------------------
@app.post("/rerank")
def rerank(request: RerankerRequest):
    model = reranker_models.get(request.model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Reranker model not found")
    with torch.no_grad():
        # Example inference: replace with your actual reranker logic
        scores = [float(model(torch.tensor([candidate]))) for candidate in request.candidates]
    return {"scores": scores}
