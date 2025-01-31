input_markdown_text = """
{Input markdown text here}
"""

# Define the task in the prompt
prompt = f"""
Please process the following markdown text and generate the top 10 chunks from the content. 
Each chunk should be a plain text portion that can be used for retrieval-augmented generation (RAG). 
If there are tables, each row should be split into separate chunks. 
Prioritize sections or paragraphs with significant content, and include as much detail as possible.

Input:
{input_markdown_text}

Return the chunks as a list of strings like this:

```json
[
  "Chunk 1 text...",
  "Chunk 2 text...",
  "Chunk 3 text...",
  "Chunk 4 text...",
  "Chunk 5 text...",
  "Chunk 6 text...",
  "Chunk 7 text...",
  "Chunk 8 text...",
  "Chunk 9 text...",
  "Chunk 10 text..."
]
