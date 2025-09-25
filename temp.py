RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
from client import MultiModelClient

# Initialize client
client = MultiModelClient(base_url="http://localhost:8000")

# -------------------------
# Health check
# -------------------------
health = client.health()
print("Health status:", health)

# -------------------------
# Embeddings
# Single text
single_emb = client.embed("This is a single text", "embedding_model_1")
print("Single text embedding:", single_emb)

# Multiple texts
texts = ["First text", "Second text"]
batch_emb = client.embed(texts, "embedding_model_1")
print("Batch embeddings:", batch_emb)

# -------------------------
# Reranking
query = "Which candidate is best?"
candidates = ["Candidate 1", "Candidate 2", "Candidate 3"]
scores = client.rerank(query, candidates, "reranker_model_1")
print("Reranker scores:", scores)
