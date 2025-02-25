import torch
from PIL import Image
import base64
import os
import io
import pandas as pd
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from unsloth import FastVisionModel

# Configuration Variables
MODEL_NAME = "unsloth/Llama-3.2-11B-Vision-Instruct"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_RETRIEVAL_COUNT = 3

# Load Models Globally
def initialize_system():
    global vision_model, vision_tokenizer, embedding_model, chroma_client
    
    # Load Vision Model
    vision_model, vision_tokenizer = FastVisionModel.from_pretrained(
        MODEL_NAME, load_in_4bit=True, device_map="auto"
    )
    FastVisionModel.for_inference(vision_model)
    
    # Load Embedding Model
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # Initialize ChromaDB Client
    chroma_client = chromadb.PersistentClient("./chromadb_store")
    print("Models and ChromaDB initialized successfully.")

# Function to Process Base64 Image
def process_base64_image(base64_string):
    try:
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return image
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# Function to Extract Text from Slides
def process_ppt_slides(dataframe, batch_size=3):
    extracted_data = []
    
    for i in range(0, len(dataframe), batch_size):
        batch = dataframe.iloc[i:i+batch_size]
        images = [process_base64_image(row["Base64Data"]) for _, row in batch.iterrows() if row["Base64Data"]]
        slide_numbers = batch["SlideNumber"].tolist()
        
        if not images:
            print(f"Skipping batch {i} due to missing images.")
            continue

        extracted_text = generate_prompt(images)
        
        for idx, slide_number in enumerate(slide_numbers):
            slide_content_encoded = embed_text(extracted_text) if extracted_text else np.zeros(512)
            extracted_data.append({
                "SlideNumber": slide_number,
                "ExtractedText": extracted_text if extracted_text else "Extraction failed",
                "Base64Image": batch.iloc[idx]["Base64Data"] if batch.iloc[idx]["Base64Data"] else "",
                "SlideContentEncoded": slide_content_encoded
            })
    
    return pd.DataFrame(extracted_data)

# Function to Generate Prompt for Multiple Images
def generate_prompt(images):
    if not images:
        return ""
    
    prompt_image = (
        "Extract all available information from this PowerPoint slide without adding any interpretations, assumptions, or extra details.\n\n"
        "Respond in the following structured format. If a section is not present in the slide, completely omit that field from the response:\n\n"
        "Title: [Extracted Slide Title]\n"
        "Headings: [List of Main Headings]\n"
        "Bullet Points: [List of Key Bullet Points]\n"
        "Tables: [Extracted Table Data exactly as it appears]\n"
        "Graphs: [Detailed description of graphs, including key data insights]\n"
        "Figures & Images: [Summarize any figures or images present]\n\n"
        "**Final Summary:** Provide a **neutral, fact-based** summary of what this slide conveys in one paragraph. Do NOT add interpretations or insights beyond the provided data.\n\n"
        "**Important:** Only return the extracted content. Do NOT include empty fields or placeholders for missing data. If a section does not exist in the slide, do not mention it."
    )
    
    image_contents = [{"type": "image"} for _ in images]
    
    messages = [{"role": "user", "content": image_contents + [{"type": "text", "text": prompt_image}]}]
    
    input_text = vision_tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    
    inputs = vision_tokenizer(
        images=images,
        text=input_text,
        add_special_tokens=False,
        return_tensors="pt"
    ).to("cuda")
    
    output_ids = vision_model.generate(**inputs, max_new_tokens=8000, use_cache=True, temperature=1.0)
    response_text = vision_tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    return response_text

# Function to Embed Text
def embed_text(text):
    if not text:
        return np.zeros(512)
    return embedding_model.encode(text, convert_to_numpy=True)

# Function to Find Relevant Slides
def find_top_n_slides(query, slides_df, top_n=CHUNK_RETRIEVAL_COUNT):
    query_embedding = embed_text(query)
    if np.all(query_embedding == 0):
        print("Query encoding failed. Returning empty results.")
        return pd.DataFrame()
    
    slides_df["Similarity"] = slides_df["SlideContentEncoded"].apply(lambda x: np.dot(x, query_embedding) if isinstance(x, np.ndarray) else 0)
    top_n_indices = slides_df["Similarity"].nlargest(top_n).index
    
    return slides_df.iloc[top_n_indices]

# Function for Query Processing and Response Generation
def query_pipeline(user_query, slides_df):
    relevant_slides = find_top_n_slides(user_query, slides_df)
    if relevant_slides.empty:
        print("No relevant slides found.")
        return []
    return relevant_slides["Base64Image"].tolist()

# Function to Generate Response from Vision Model
def generate_response_from_images(images, user_query):
    if not images:
        return "No relevant images found."
    
    image_contents = [{"type": "image"} for _ in images]
    messages = [{"role": "user", "content": image_contents + [{"type": "text", "text": user_query}]}]
    
    input_text = vision_tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    
    inputs = vision_tokenizer(
        images=images,
        text=input_text,
        add_special_tokens=False,
        return_tensors="pt"
    ).to("cuda")
    
    output_ids = vision_model.generate(**inputs, max_new_tokens=8000, use_cache=True, temperature=1.0)
    response_text = vision_tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    return response_text

# Main Execution Flow
initialize_system()
slides_df = process_ppt_slides(your_dataframe)

user_query = "Summarize the key findings from the financial report slides."
retrieved_images_base64 = query_pipeline(user_query, slides_df)

if retrieved_images_base64:
    retrieved_images = [process_base64_image(img) for img in retrieved_images_base64 if img]
    model_response = generate_response_from_images(retrieved_images, user_query)
else:
    model_response = "No relevant images found."

print(model_response)
