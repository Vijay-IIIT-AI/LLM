
Function:

run_translation(mode, source, output=None, target_lang="Korean", max_slides=None)

[1] mode → what type of input ("pptx", "file", or "text")
[2] source → the thing to translate (file path or text string)
[3] output → where to save result (pptx/txt file path). Optional for text mode
[4] target_lang → language to translate into (default: Korean)
[5] max_slides → limit number of slides to translate in PPTX (default: all)

Postive Case:
-------------

Type 1:( When user Give only text)

Input:
run_translation("text", "What are you doing?", target_lang="Korean")

Output Expected:
{'status': 'completed', 'message': None, 'translated_content': '무엇을 하고 계세요?'}

Type 2: (When  User Give Pptx file) (ppt file is not supported on pptx is supported)
------------

Input:
run_translation("pptx", r"/content/Final_Review_PPT_2.pptx", "output_ko.pptx", target_lang="Korean"))

Output Expected:
{'status': 'completed', 'message': None, 'translated_content': 'output_ko.pptx'}


Type 3: (When User Uploads a txt File) 
---------------------------------

Input:
print(run_translation("file", r"/content/sample.txt", "/content/output_ta.txt", target_lang="Korean"))


Output Expected:
{'status': 'completed', 'message': None, 'translated_content': '/content/output_ta.txt'}


Negative Case:
--------------

{'status': 'failed', 'message': "[Errno 2] No such file or directory: '/content/sampe.txt'", 'translated_content': None}

{'status': 'failed', 'message': "Package not found at '/content/MachineLearning.ppt'", 'translated_content': None}



from pptx import Presentation
import requests
import time
import re
import os

# ==========================
# CONFIG
# ==========================
api_key = "mjLoMvjl6nnvofomLxPNDMWZsvuouvCz"
API_URL = "https://api.mistral.ai/v1/chat/completions"  # replace with your API endpoint


# ==========================
# Translation Core
# ==========================
def translate(text_or_list, tgt: str = "Korean"):
    if isinstance(text_or_list, str):
        inputs = [text_or_list]
    elif isinstance(text_or_list, list):
        inputs = text_or_list
    else:
        return {"status": "failed", "message": "translate() accepts str or list of str", "translated_content": None}

    inputs_clean, idx_map = [], []
    for i, t in enumerate(inputs):
        if not t.strip() or is_url(t) or is_symbolic(t):
            continue
        inputs_clean.append(t)
        idx_map.append(i)

    if not inputs_clean:
        return {"status": "completed", "message": None, "translated_content": text_or_list}

    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "system",
                "content": f"You are a professional translator. Translate strictly into {tgt}. "
                           f"Only return translated text. No explanations, notes, or formatting."
            },
            {
                "role": "user",
                "content": "\n".join(inputs_clean)
            }
        ]
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        time.sleep(1)
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        translated_lines = resp.json()["choices"][0]["message"]["content"].strip().split("\n")
    except Exception as e:
        return {"status": "failed", "message": str(e), "translated_content": None}

    results = list(inputs)
    for idx, trans in zip(idx_map, translated_lines):
        results[idx] = trans.strip()

    final = results if isinstance(text_or_list, list) else results[0]
    return {"status": "completed", "message": None, "translated_content": final}


# ==========================
# Helpers
# ==========================
def is_symbolic(text: str) -> bool:
    if not text.strip():
        return True
    non_alpha_ratio = sum(1 for c in text if not c.isalpha()) / len(text)
    if non_alpha_ratio > 0.7:
        return True
    if len(text) <= 3:
        return True
    if re.match(r"^[\W_0-9=+\-*/|^<>{}\[\]]+$", text):
        return True
    return False

def is_url(text: str) -> bool:
    return bool(re.match(r"https?://\S+", text.strip()))

def chunk_text(lines, chunk_size=20):
    for i in range(0, len(lines), chunk_size):
        yield lines[i:i + chunk_size]


# ==========================
# PPTX Translation (batched)
# ==========================
def collect_texts_from_pptx(prs, max_slides=None):
    texts, locations = [], []
    for slide_idx, slide in enumerate(prs.slides, start=1):
        if max_slides and slide_idx > max_slides:
            break

        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    full_text = "".join(run.text for run in para.runs).strip()
                    if full_text and not is_symbolic(full_text) and not is_url(full_text):
                        texts.append(full_text)
                        locations.append(para)

            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        if cell.text_frame:
                            for para in cell.text_frame.paragraphs:
                                full_text = "".join(run.text for run in para.runs).strip()
                                if full_text and not is_symbolic(full_text) and not is_url(full_text):
                                    texts.append(full_text)
                                    locations.append(para)
    return texts, locations

def write_translations_to_pptx(translated, locations):
    for t, para in zip(translated, locations):
        for run in para.runs:
            run.text = ""
        if para.runs:
            para.runs[0].text = t
        else:
            para.text = t

def translate_pptx_fast(input_pptx, output_pptx, target_lang="Korean", max_slides=None):
    try:
        prs = Presentation(input_pptx)
        texts, locations = collect_texts_from_pptx(prs, max_slides)
        print(f"Collected {len(texts)} text blocks")

        translated = []
        for chunk in chunk_text(texts, 20):
            chunk_result = translate(chunk, target_lang)
            if chunk_result["status"] == "failed":
                return chunk_result
            translated.extend(chunk_result["translated_content"])

        write_translations_to_pptx(translated, locations)
        prs.save(output_pptx)
        print(f"Saved translated PPTX as {output_pptx}")
        return {"status": "completed", "message": None, "translated_content": output_pptx}
    except Exception as e:
        return {"status": "failed", "message": str(e), "translated_content": None}


# ==========================
# TXT Translation
# ==========================
def translate_text_lines(lines, target_lang="Korean"):
    results = []
    for chunk in chunk_text(lines):
        chunk_result = translate(chunk, target_lang)
        if chunk_result["status"] == "failed":
            return chunk_result
        results.extend(chunk_result["translated_content"])
    return {"status": "completed", "message": None, "translated_content": results}

def translate_text_input(text, target_lang="Korean"):
    lines = text.strip().split("\n")
    result = translate_text_lines(lines, target_lang)
    if result["status"] == "failed":
        return result
    return {"status": "completed", "message": None, "translated_content": "\n".join(result["translated_content"])}

def translate_text_file(input_file, output_file, target_lang="Korean"):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        result = translate_text_lines(lines, target_lang)
        if result["status"] == "failed":
            return result

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(result["translated_content"]))

        print(f"Saved translated text file as {output_file}")
        return {"status": "completed", "message": None, "translated_content": output_file}
    except Exception as e:
        return {"status": "failed", "message": str(e), "translated_content": None}


# ==========================
# Master Pipeline
# ==========================
def run_translation(mode, source, output=None, target_lang="Korean", max_slides=None):
    try:
        if mode == "pptx":
            if not output:
                return {"status": "failed", "message": "Output pptx path required.", "translated_content": None}
            return translate_pptx_fast(source, output, target_lang, max_slides)

        elif mode == "file":
            ext = os.path.splitext(source)[1].lower()
            if ext == ".pptx":
                if not output:
                    return {"status": "failed", "message": "Output pptx path required.", "translated_content": None}
                return translate_pptx_fast(source, output, target_lang, max_slides)
            elif ext == ".txt":
                if not output:
                    return {"status": "failed", "message": "Output text file path required.", "translated_content": None}
                return translate_text_file(source, output, target_lang)
            else:
                return {"status": "failed", "message": f"Unsupported file type: {ext}", "translated_content": None}

        elif mode == "text":
            result = translate_text_input(source, target_lang)
            if output and result["status"] == "completed":
                try:
                    with open(output, "w", encoding="utf-8") as f:
                        f.write(result["translated_content"])
                    print(f"Saved translated text as {output}")
                    return {"status": "completed", "message": None, "translated_content": output}
                except Exception as e:
                    return {"status": "failed", "message": str(e), "translated_content": None}
            return result

        else:
            return {"status": "failed", "message": f"Invalid mode: {mode}", "translated_content": None}
    except Exception as e:
        return {"status": "failed", "message": str(e), "translated_content": None}


# ==========================
# Example Runs
# ==========================
if __name__ == "__main__":
    print(run_translation("pptx", r"/content/MachineLearning.ppt", "output_ko.pptx", target_lang="Korean"))
    #print(run_translation("text", "What are you doing?", target_lang="Korean"))
    #print(run_translation("file", r"/content/sample.txt", "/content/output_ta.txt", target_lang="Korean"))

