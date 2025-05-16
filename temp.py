rerank_inputs = [(user_query, c["summary"]) for c in candidates]
    reranked_scores = reranker.predict(rerank_inputs)
    sorted_candidates = sorted(zip(candidates, reranked_scores), key=lambda x: x[1], reverse=True)
