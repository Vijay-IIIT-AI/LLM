from unsloth import FastVisionModel
from transformers import TextStreamer
import torch
from PIL import Image

#LLAMA Model - "unsloth/Llama-3.2-11B-Vision-Instruct"
#Pixtral Model - ""unsloth/Pixtral-12B-Base-2409-bnb-4bit""
# Load the model in 16-bit
model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Llama-3.2-11B-Vision-Instruct",
    load_in_4bit=False,  # Use full precision (16-bit)   
    device_map="auto"
)

# Enable inference mode
FastVisionModel.for_inference(model)

image_path = r"/content/Slide2.JPG"  # Replace with your image path
image = Image.open(image_path).convert("RGB")  # Ensure image is in RGB format


prompt_image = """
    Extract all texts from this presentation slide (literal extraction, do not summarize!) and tabular data, when image or diagram is present describe it.
    When a graph with data is present, describe what it represents in detail, with key messages on data points.  When extracting texts, those that are part of a diagram or graph should be only extracted within this context, not within the "text" category.
    Give only one final json - do not give any code

    Write the extracted contents in JSON format, that will follow this structure:

    [
        {
            "heading": "Example slide heading",
            "text": "Example text on the slide"
            "images": [
                "Example image or diagram description",
                "Example image or diagram description",
                "Example image or diagram description"
            ],
            "graphs": [
                "Example graph description"
            ]
        }
    ]

    If there is any part missing (like there is no heading on the slide) - just represent it as null.
    Output the JSON file. Make sure your response is a VALID JSON! Do not put backticks around the output.

    SYNTACTICALLY CORRECT EXAMPLE RESPONSE:
    [
        {
            "slide_heading": "Ecological Threat Report 2023",
            "subheading": null,
            "text": "Key Findings\nCountry Hotspots\nEcological Threats\nMegacities\nPolicy Recommendations",
            "images": [
                "Example image"
            ],
            "graphs": []
        }
    ]
    """


# Define the instruction (Ensure to reference the image!)
instruction =  prompt_image #"Describe accurately what you see in this image."

# # Format input as a chat message
# messages = [
#     {"role": "user", "content": [
#         {"type": "text", "text": instruction},  # Ensure <image> token is included
#         {"type": "image", "image": image}  # Image must be passed separately
#     ]}
# ]

messages = [
    {"role": "user", "content": [
        {"type": "image"},
        {"type": "text", "text": instruction}
    ]}
]

# Convert messages into a format the model understands
input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

# Tokenize the input (text + image)
inputs = tokenizer(
    images=[image],  # Pass image as a list
    text=input_text,  # Ensure the text references the image
    add_special_tokens=False,
    return_tensors="pt"
).to("cuda")


output_ids = model.generate(**inputs, max_new_tokens=300, use_cache=True, temperature=1.0)
# Decode the output to get plain text
response_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
# Print the response
print("Model Response:\n", response_text)
