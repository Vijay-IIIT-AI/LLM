from langchain.text_splitter import RecursiveCharacterTextSplitter

# Example markdown text
markdown_text = """


"""

# Initialize the RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=100,
    length_function=len,
    separators=["\n## ", "\n### ", "\n\n", "\n"]
)

# Chunk the markdown text
chunks = splitter.split_text(markdown_text)

# Print the chunks
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}:\n{chunk}\n")
