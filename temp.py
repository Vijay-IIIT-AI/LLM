import requests
from typing import List, Union, Dict

class MultiModelClient:
    """
    Python client for GPU Multi-Model FastAPI service.
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -------------------------
    # Embedding API
    # -------------------------
    def embed(self, texts: Union[str, List[str]], model_name: str) -> List[List[float]]:
        """
        Get embeddings for a single text or a list of texts using specified embedding model.
        Returns a list of embeddings (each embedding is a list of floats).
        """
        if isinstance(texts, str):
            texts = [texts]
        payload = {
            "model_name": model_name,
            "texts": texts
        }
        try:
            response = requests.post(f"{self.base_url}/embed", json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if "embeddings" not in data:
                raise ValueError("Invalid response: missing embeddings")
            return data["embeddings"]
        except Exception as e:
            raise RuntimeError(f"Embedding API call failed: {e}")

    # -------------------------
    # Reranker API
    # -------------------------
    def rerank(self, query: str, candidates: List[str], model_name: str) -> List[float]:
        """
        Rerank candidates for a given query using specified reranker model.
        Returns a list of scores (one score per candidate).
        """
        if not isinstance(candidates, list) or len(candidates) == 0:
            raise ValueError("Candidates must be a non-empty list of strings")

        payload = {
            "model_name": model_name,
            "query": query,
            "candidates": candidates
        }
        try:
            response = requests.post(f"{self.base_url}/rerank", json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if "scores" not in data:
                raise ValueError("Invalid response: missing scores")
            return data["scores"]
        except Exception as e:
            raise RuntimeError(f"Reranker API call failed: {e}")

    # -------------------------
    # Health Check
    # -------------------------
    def health(self) -> Dict:
        """
        Check API health status.
        Returns a dictionary with status info.
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Health check failed: {e}")
