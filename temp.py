# RAG Pipeline for Confluence Page Retrieval with Page ID Resolution
# Step-by-step: Summary Matching -> Page ID Identification -> Chunk Retrieval -> Answer Generation

from sentence_transformers import SentenceTransformer, util
import pandas as pd
import faiss
import numpy as np
from typing import List, Dict
import openai
import torch
from rerankers import Reranker  # Install via: pip install rerankers

# -----------------------
# Load your DataFrame
# -----------------------
df = pd.read_json("confluence_pages.json")  # Should contain: page_id, page_title, summary (list), entities, page_content

# -----------------------
# Embedding Setup
# -----------------------
model = SentenceTransformer("all-MiniLM-L6-v2")  # You can replace with OpenAI or other models
reranker = Reranker("cross-encoder/ms-marco-MiniLM-L-6-v2")

df["summary_text"] = df["summary"].apply(lambda bullets: " ".join(bullets))
summary_embeddings = model.encode(df["summary_text"].tolist(), show_progress_bar=True, convert_to_tensor=True)

# -----------------------
# Stage 1: Identify Page(s) via Summary
# -----------------------
def identify_pages(user_query: str, top_n=10) -> List[str]:
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(query_embedding, summary_embeddings)[0]
    top_results = torch.topk(cosine_scores, k=top_n)

    candidates = []
    for score, idx in zip(top_results.values, top_results.indices):
        page_id = df.iloc[idx]["page_id"]
        summary = df.iloc[idx]["summary_text"]
        candidates.append({"page_id": page_id, "summary": summary})

    # Rerank using cross-encoder
    reranked = reranker.rerank(user_query, [c["summary"] for c in candidates])
    sorted_candidates = sorted(zip(candidates, reranked), key=lambda x: x[1], reverse=True)
    return [(c["page_id"], c["summary"]) for c, _ in sorted_candidates[:5]]

# -----------------------
# Ask LLM to Confirm Pages
# -----------------------
def confirm_page_ids(user_query: str, page_candidates: List[tuple]) -> List[str]:
    summary_block = "\n\n".join([f"Page ID: {pid}\nSummary: {summary}" for pid, summary in page_candidates])

    system_prompt = """You are an assistant identifying the most relevant Confluence pages for a user's question based on page summaries. Respond only with a list of relevant Page IDs. If multiple pages are relevant, include them all."""

    user_prompt = f"""
User Question: {user_query}

Available Pages:
{summary_block}

Which page IDs are most relevant to the user's query?
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip().split()

# -----------------------
# Chunking Function (Markdown-aware)
# -----------------------
def chunk_text(text: str, max_tokens=400) -> List[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len((current_chunk + para).split()) > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += "\n\n" + para
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# -----------------------
# Final Query with Selected Pages
# -----------------------
def final_query_response(user_query: str, selected_page_ids: List[str], top_k_chunks=3):
    relevant_chunks = []
    query_embedding = model.encode([user_query], convert_to_tensor=True)

    for pid in selected_page_ids:
        page_row = df[df["page_id"] == pid].iloc[0]
        content = page_row["page_content"]
        chunks = chunk_text(content)
        chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
        top_indices = scores.argsort(descending=True)[:top_k_chunks]
        relevant_chunks.extend([chunks[i] for i in top_indices])

    final_context = "\n\n".join(relevant_chunks)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering questions based on Confluence documentation."},
            {"role": "user", "content": f"Answer the question using this context:\n\n{final_context}\n\nQuestion: {user_query}"}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# -----------------------
# Example Usage
# -----------------------
user_query = "What are the key risks and action items mentioned for Project Apollo in Q3?"
page_candidates = identify_pages(user_query)
confirmed_ids = confirm_page_ids(user_query, page_candidates)
answer = final_query_response(user_query, confirmed_ids)
print("Answer:\n", answer)
