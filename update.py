from unsloth import FastVisionModel
from transformers import TextStreamer
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
import numpy as np

# Load Vision LLM model
model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Llama-3.2-11B-Vision-Instruct",
    load_in_4bit=True,
    device_map="auto"
)
FastVisionModel.for_inference(model)

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to process image
def process_image(image_path):
    image = Image.open(image_path).convert("RGB")
    return image

# Function to generate structured text from slide image
def extract_text_from_image(image):
    prompt = """
    Extract all key information from this PowerPoint slide. Provide structured output in the following format:

    Title: [Extracted Slide Title]
    Headings: [List of Main Headings]
    Bullet Points: [List of Key Bullet Points]
    Tables: [Extracted Table Data]
    Graphs: [Description of Graphs and Key Insights]
    Figures & Images: [Summary of Any Figures or Images]

    Ensure the output is detailed and structured, making it useful for retrieval and Q&A.
    """

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

    inputs = tokenizer(
        images=[image],
        text=input_text,
        add_special_tokens=False,
        return_tensors="pt"
    ).to("cuda")

    output_ids = model.generate(**inputs, max_new_tokens=300, use_cache=True, temperature=1.0)
    response_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return response_text

# Function to embed extracted text
def embed_text(text):
    return embedding_model.encode(text, convert_to_numpy=True)

# Function to find top-N relevant slides
def find_top_n_slides(query, slides_text, slides_images, top_n=3):
    query_embedding = embed_text(query)
    slides_embeddings = np.array([embed_text(text) for text in slides_text])

    similarities = np.dot(slides_embeddings, query_embedding)  # Cosine similarity
    top_n_indices = np.argsort(similarities)[-top_n:][::-1]

    return [(slides_text[i], slides_images[i]) for i in top_n_indices]

# Main processing loop
slides = ["slide1.jpg", "slide2.jpg", "slide3.jpg"]  # Replace with actual slide paths
extracted_texts = []
slide_images = []

for slide in slides:
    img = process_image(slide)
    text = extract_text_from_image(img)
    extracted_texts.append(text)
    slide_images.append(img)

# Example query for retrieval
query = "Summarize the key financial data from the slides."
top_slides = find_top_n_slides(query, extracted_texts, slide_images, top_n=3)

# Pass top slides to LLM for final Q&A
final_context = "\n\n".join([text for text, _ in top_slides])
answer = extract_text_from_image(final_context)  # Reuse function for Q&A

print("Final Answer:\n", answer)
