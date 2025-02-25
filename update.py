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

prompt_image = (
    "Extract all available information from this PowerPoint slide while strictly avoiding hallucinating any missing content.\n\n"
    "Provide structured output in the following format:\n\n"
    "Title: [Extracted Slide Title or null if not present]\n"
    "Headings: [List of Main Headings or null if none]\n"
    "Bullet Points: [List of Key Bullet Points or null if none]\n"
    "Tables: [Extracted Table Data exactly as it appears, or null if no tables]\n"
    "Graphs: [Detailed description of graphs, including key data insights, or null if no graphs]\n"
    "Figures & Images: [Summarize any figures or images present, or null if none]\n\n"
    "**Final Summary:** Provide a concise, well-structured explanation of what this slide conveys in a single paragraph.\n\n"
    "Ensure the extracted data is precise and complete. Do not infer or generate content that is not present on the slide."
    "**Important:** Respond only with the extracted information. Do not include this prompt in the response."
)


prompt_image = (
    "Extract all texts from this presentation slide (literal extraction, do not summarize!) and tabular data. When an image or diagram is present, describe it.\n"
    "When a graph with data is present, describe what it represents in detail, with key messages on data points. When extracting texts, those that are part of a diagram or graph should be only extracted within this context, not within the 'text' category.\n"
    "Give only one final JSON - do not give any code.\n\n"
    "Write the extracted contents in JSON format, following this structure:\n\n"
    "[\n"
    "    {\n"
    "        \"heading\": \"Example slide heading\",\n"
    "        \"text\": \"Example text on the slide\",\n"
    "        \"images\": [\n"
    "            \"Example image or diagram description\",\n"
    "            \"Example image or diagram description\",\n"
    "            \"Example image or diagram description\"\n"
    "        ],\n"
    "        \"graphs\": [\n"
    "            \"Example graph description\"\n"
    "        ]\n"
    "    }\n"
    "]\n\n"
    "If there is any part missing (like there is no heading on the slide), just represent it as null.\n"
    "Output the JSON file. Make sure your response is a VALID JSON! Do not put backticks around the output.\n\n"
    "SYNTACTICALLY CORRECT EXAMPLE RESPONSE:\n"
    "[\n"
    "    {\n"
    "        \"slide_heading\": \"Ecological Threat Report 2023\",\n"
    "        \"subheading\": null,\n"
    "        \"text\": \"Key Findings\\nCountry Hotspots\\nEcological Threats\\nMegacities\\nPolicy Recommendations\",\n"
    "        \"images\": [\n"
    "            \"Example image\"\n"
    "        ],\n"
    "        \"graphs\": []\n"
    "    }\n"
    "]"
)

