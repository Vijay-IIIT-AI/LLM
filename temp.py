from sentence_transformers import SentenceTransformer, CrossEncoder, util

# Step 1: Load models
retriever = SentenceTransformer("paraphrase-MiniLM-L6-v2")
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")  # Can swap with jinaai/jina-reranker-v2-base-multilingual

# Step 2: Define documents
docs = [
    "서울은 한국의 수도이다.",
    "Seoul is the capital of South Korea.",
    "한국의 봄은 매우 아름답다.",
    "Spring in Korea is very beautiful.",
    "The Eiffel Tower is located in Paris."
]

# Step 3: Define query
query = "한국의 수도는 어디인가요?"

# Step 4: Retrieve top-k candidates using bi-encoder
doc_embeddings = retriever.encode(docs, convert_to_tensor=True)
query_embedding = retriever.encode([query], convert_to_tensor=True)
similarity_scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]

# Step 5: Select top N candidates
top_k = 3  # Configurable
top_indices = similarity_scores.topk(top_k).indices
top_docs = [docs[i] for i in top_indices]
top_doc_scores = [similarity_scores[i].item() for i in top_indices]

print("\n🔍 Top Retrieved Documents (Bi-Encoder):")
for doc, score in zip(top_docs, top_doc_scores):
    print(f"Score: {score:.4f} - {doc}")

# Step 6: Prepare input for reranker (query, doc) pairs
reranker_inputs = [(query, doc) for doc in top_docs]

# Step 7: Rerank using cross-encoder
rerank_scores = reranker.predict(reranker_inputs)

# Step 8: Sort by reranker score
final_ranking = sorted(zip(top_docs, rerank_scores), key=lambda x: x[1], reverse=True)

print("\n🏆 Final Reranked Documents (Cross-Encoder):")
for doc, score in final_ranking:
    print(f"Score: {score:.4f} - {doc}")
