import chromadb
from minillm import MiniLLM
import numpy as np

# Example data (replace these with your actual lists)
list1 = ["page1", "page2", "page3"]  # Page IDs
list2 = ["This is the content of page 1", "Content of page 2", "Content of page 3"]  # Page content (chunks)
list4 = ["text", "table", "text"]  # Meta data (type of content)

# Initialize Chroma client and MiniLLM
client = chromadb.Client()
llm = MiniLLM()

# Create or get a Chroma collection
collection = client.create_collection("page_collection")

# Function to encode content using MiniLLM
def encode_content(content_list):
    return [llm.encode(content) for content in content_list]

# Encode the page content (list2)
encoded_content = encode_content(list2)

# Add pages to the Chroma collection
for i, (page_id, encoded_chunk, meta) in enumerate(zip(list1, encoded_content, list4)):
    collection.add(
        ids=[page_id],
        embeddings=[encoded_chunk],
        metadatas=[{"content_type": meta}],
        documents=[list2[i]],
    )

# Function to retrieve top 10 relevant chunks
def retrieve_top_chunks(query, top_k=10):
    # Encode the query
    query_embedding = llm.encode(query)
    
    # Perform the retrieval
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results

# Example usage
query = "Search for relevant content regarding page 1"
top_chunks = retrieve_top_chunks(query)

# Print the top 10 results
for idx, result in enumerate(top_chunks["documents"]):
    print(f"Rank {idx+1}: {result}")
