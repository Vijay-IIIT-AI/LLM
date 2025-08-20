pptx_path = r"/content/ML.pptx"

from docling.document_converter import DocumentConverter

# 1) Convert the PPTX using Docling
converter = DocumentConverter()
res = DocumentConverter().convert(pptx_path)
doc = res.document
original_texts = [item.text for item in doc.texts]
print("Extracted texts:", original_texts)

# Step 2️⃣: Translate mapping (replace translate() with your API logic)
from tqdm import tqdm

translation_map = {}
for txt in tqdm(original_texts, desc="Translating PPT Text", unit="text"):
    translation_map[txt] = translate(txt)

from pptx import Presentation
import time


# Step 3️⃣: Replace text in PPTX preserving formatting
prs = Presentation(pptx_path)
for slide in prs.slides:
    print("Running Slide:", slide)
    time.sleep(5)

    for shape in slide.shapes:
        # Text box content
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    orig = run.text.strip()
                    if orig in translation_map:
                        run.text = translation_map[orig]

        # Table cell content
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for para in cell.text_frame.paragraphs:
                        for run in para.runs:
                            orig = run.text.strip()
                            if orig in translation_map:
                                run.text = translation_map[orig]

# Save your translated PPTX
prs.save("/content/output_translated_KR.pptx")
print("Saved as output_translated.pptx")

import os
import requests
from time import sleep

api_key = 

def translate(text: str, tgt: str = "Korean") -> str:
    sleep(10)
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": f"You are a professional Korean translator to {tgt}.Just translate what is there don't give any extra information your just translator"},
            {"role": "user", "content": text}
        ]
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# Test
print(translate("Hello, how are you?", "Korean"))
