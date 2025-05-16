# RAG Pipeline: Query Rewriting + Hybrid Retrieval (Dense + Sparse + Reranker)

import requests
import pandas as pd
from sentence_transformers import SentenceTransformer, CrossEncoder, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.documents import Document
import torch
import json
import re

# ----------------------------
# Sample Documents
# ----------------------------
# ----------------------------
# Sample Documents (more complex)
# ----------------------------

docs = [
    Document(page_content="""
Milestone 1 was completed by the frontend team, including extensive UI fixes and integration tests. The team utilized React 18 with hooks and context APIs to improve component modularity. Automated tests were written using Jest and Cypress for both unit and end-to-end validations. Deployment occurred in a Docker container orchestrated by Kubernetes, ensuring scalability and easy rollbacks. During the sprint, cross-team communication with backend engineers improved the API schema documentation, reducing integration bugs. Performance benchmarks showed a 15% faster load time compared to the previous release. User feedback was collected through in-app surveys, highlighting usability improvements and remaining issues. The DevOps team monitored logs and metrics to ensure stability post-release. Documentation was updated in Confluence with detailed release notes and troubleshooting tips. The team is now preparing for Milestone 2 with a focus on accessibility enhancements and mobile responsiveness.
"""),

    Document(page_content="""
The security team is currently reviewing compliance protocols for milestone 2, collaborating closely with the legal department to ensure all regulatory requirements are met. This includes GDPR adherence, data encryption standards, and multi-factor authentication implementations. Threat modeling exercises were conducted to identify potential vulnerabilities in the authentication workflows. Penetration testing is scheduled for the next sprint, with external auditors invited to review the system. The team also updated firewall configurations and Intrusion Detection System (IDS) rules to mitigate recent cyberattack trends. Incident response playbooks were revised for better clarity and faster mitigation. Training sessions on security best practices were held for all developers, emphasizing secure coding standards. The compliance team is preparing documentation for ISO 27001 certification, focusing on risk assessment and asset management. Regular audits and continuous monitoring are planned to maintain compliance throughout the project lifecycle. Additionally, disaster recovery plans are being refined to include cloud backup strategies and failover testing.
"""),

    Document(page_content="""
Last week, the backend team successfully deployed the new payment gateway API to the staging environment. This API supports multiple payment methods, including credit cards, digital wallets, and bank transfers, with enhanced fraud detection mechanisms. The team implemented OAuth 2.0 for secure token-based authentication and improved API rate limiting to prevent abuse. The database schema was optimized for transaction logging, utilizing partitioned tables and indexing strategies to enhance query performance. Integration with third-party payment providers was tested extensively, ensuring fallback mechanisms are in place. Monitoring dashboards were set up with Prometheus and Grafana to track latency, error rates, and throughput. Automated rollback scripts were prepared in case of deployment failures. Coordination with the frontend team ensured that UI components correctly handle API responses and errors. The backend also includes detailed audit trails to comply with financial regulations. Next steps involve load testing and preparing documentation for the API consumers.
"""),

    Document(page_content="""
A delay occurred in deployment due to unresolved bugs found during Quality Assurance (QA). The QA team identified several critical issues, including memory leaks in the data processing module and race conditions in concurrent user sessions. Bug reports were logged in Jira with priority levels assigned based on impact and frequency. The development team is actively reproducing and fixing these issues, with code reviews and pair programming sessions to prevent regressions. Automated testing pipelines were updated to include scenarios that previously failed. Root cause analysis pointed to improper thread synchronization and inefficient resource management. Communication between QA and development teams was enhanced with daily stand-ups and detailed bug triage meetings. The deployment schedule has been adjusted to allow sufficient time for verification. Stakeholders were informed of the delay with revised timelines and impact assessments. Efforts are also underway to improve logging and monitoring to detect similar issues earlier in future cycles.
"""),

    Document(page_content="""
The queen's historical rights were discussed during the leadership seminar about monarchy law and its evolution over centuries. The seminar explored various legal precedents affecting royal privileges, property rights, and succession laws. Comparative analysis was made between different monarchies and how constitutional reforms have shifted power balances. The impact of landmark cases, royal charters, and parliamentary acts on limiting or expanding the queen’s authority was examined. Discussions included the sociopolitical context influencing monarchy laws, such as the role of public opinion, media, and international relations. Legal scholars presented on topics like sovereign immunity, prerogative powers, and ceremonial duties. The session concluded with debates on the relevance of monarchy rights in modern democracies and potential future reforms. Attendees included historians, legal experts, and political scientists, fostering multidisciplinary perspectives. Documentation of the seminar will be published in the upcoming law journal issue. This seminar series aims to bridge the gap between historical legal traditions and contemporary governance challenges.
"""),
]



doc_texts = [doc.page_content for doc in docs]

# ----------------------------
# Embedding & Reranker Models
# ----------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# ----------------------------
# TF-IDF (Sparse Vectorizer)
# ----------------------------
tfidf_vectorizer = TfidfVectorizer().fit(doc_texts)
tfidf_matrix = tfidf_vectorizer.transform(doc_texts)

# ----------------------------
# Query Rewriter (Mistral API)
# ----------------------------
def rewrite_query(user_question: str) -> dict:
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer kRDWlPq3XuZmUYPW3oUtWqjQrvR2RNyG",
        "Content-Type": "application/json"
    }
    prompt = f"""
You are a smart assistant in a document search system.
Given a user query, extract:
- A simplified rewritten version of the query for better sparse retrieval
- A list of key tags or terms for dense retrieval
Return it in the following JSON format:
{{"rewritten_query": "...", "key_tags": ["...", "..."]}}
User query: "{user_question}"
"""
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.5
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    match = re.search(r"\{.*\}", content, re.DOTALL)
    return json.loads(match.group()) if match else {"rewritten_query": user_question, "key_tags": []}

# ----------------------------
# Hybrid Retrieval Function
# ----------------------------
def hybrid_retrieve(user_query: str, top_k: int = 3):
    rewritten = rewrite_query(user_query)
    print("\n--- Query Rewrite ---")
    print("Rewritten:", rewritten)

    sparse_q = rewritten["rewritten_query"]
    dense_tags = " ".join(rewritten["key_tags"])

    # Dense Embedding Search
    dense_embedding = embedding_model.encode(dense_tags, convert_to_tensor=True)
    doc_embeddings = embedding_model.encode(doc_texts, convert_to_tensor=True)
    dense_scores = util.pytorch_cos_sim(dense_embedding, doc_embeddings)[0].cpu().numpy()
    print("\n--- Dense Scores ---")
    for i, score in enumerate(dense_scores):
        print(f"{i}: {doc_texts[i]} (score: {score:.4f})")

    # Sparse Search
    sparse_vec = tfidf_vectorizer.transform([sparse_q])
    sparse_scores = cosine_similarity(sparse_vec, tfidf_matrix).flatten()
    print("\n--- Sparse Scores ---")
    for i, score in enumerate(sparse_scores):
        print(f"{i}: {doc_texts[i]} (score: {score:.4f})")

    # Combine Scores
    combined_scores = 0.7 * dense_scores + 0.3 * sparse_scores
    top_indices = combined_scores.argsort()[::-1][:top_k * 2]

    # Rerank
    candidates = [(i, doc_texts[i]) for i in top_indices]
    rerank_inputs = [(user_query, content) for _, content in candidates]
    rerank_scores = reranker.predict(rerank_inputs)
    reranked = sorted(zip(candidates, rerank_scores), key=lambda x: x[1], reverse=True)

    print("\n--- Reranked Results ---")
    for ((idx, content), score) in reranked[:top_k]:
        print(f"Index: {idx} | Score: {score:.4f} | Content: {content}")

    return [{"index": idx, "content": content} for ((idx, content), _) in reranked[:top_k]]

# ----------------------------
# Test Example
# ----------------------------
query = "payment?"
results = hybrid_retrieve(query)
print(f"Query: {query}")
print("Top documents:")
for res in results:
    print(f"Index: {res['index']} - Content: {res['content']}")
