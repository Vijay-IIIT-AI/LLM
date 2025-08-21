from pptx import Presentation
import requests
import time
import re
import os

# --------------------------
# Translation API
# --------------------------
def translate(text: str, tgt: str = "Korean") -> str:
    if not text.strip():
        return text

    # If the whole text is a URL -> skip translation
    if is_url(text):
        return text

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "system",
                "content": f"You are a professional translator. Translate the following strictly into {tgt}. "
                           f"Only return translated text. Do not add explanations, notes, or formatting."
            },
            {"role": "user", "content": text}
        ]
    }

    try:
        time.sleep(1)  # avoid hitting rate limits
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Translation error for: '{text[:50]}...' -> {e}")
        return text  # fallback


# --------------------------
# Symbol / Math / URL Detector
# --------------------------
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


# --------------------------
# Translate Paragraph (pptx)
# --------------------------
def translate_paragraph_preserve_runs(para, target_lang="Korean"):
    for run in para.runs:
        text = run.text
        if not text.strip():
            continue
        if is_symbolic(text) or is_url(text):
            continue  # skip symbols and URLs
        run.text = translate(text, target_lang)


# --------------------------
# PPTX Translation
# --------------------------
def translate_pptx(input_pptx, output_pptx, target_lang="Korean", max_slides=None):
    prs = Presentation(input_pptx)
    for slide_idx, slide in enumerate(prs.slides, start=1):
        if max_slides and slide_idx > max_slides:
            break
        print(f"Processing Slide {slide_idx}/{len(prs.slides)}")

        try:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        translate_paragraph_preserve_runs(para, target_lang)

                if shape.has_table:
                    for row in shape.table.rows:
                        for cell in row.cells:
                            if cell.text_frame:
                                for para in cell.text_frame.paragraphs:
                                    translate_paragraph_preserve_runs(para, target_lang)
        except Exception as e:
            print(f"Error while processing Slide {slide_idx}: {e}. Skipping this slide.")
            continue

    prs.save(output_pptx)
    print(f"Saved translated PPTX as {output_pptx}")


# --------------------------
# Text Translation (string or file)
# --------------------------
def chunk_text(lines, chunk_size=20):
    """Split lines into groups to avoid large requests"""
    for i in range(0, len(lines), chunk_size):
        yield lines[i:i + chunk_size]


def translate_text_lines(lines, target_lang="Korean"):
    results = []
    for chunk in chunk_text(lines):
        translated_chunk = []
        to_translate = []
        idx_map = []

        # Separate URLs from normal text
        for i, line in enumerate(chunk):
            if is_url(line):
                translated_chunk.append(line)  # keep as-is
            else:
                to_translate.append(line)
                idx_map.append(i)

        # Translate only the non-URLs
        if to_translate:
            joined = "\n".join(to_translate)
            translated = translate(joined, target_lang).split("\n")

            for pos, t in zip(idx_map, translated):
                while len(translated_chunk) <= pos:
                    translated_chunk.append("")
                translated_chunk[pos] = t

        results.extend(translated_chunk)
    return results


def translate_text_input(text, target_lang="Korean"):
    lines = text.strip().split("\n")
    return "\n".join(translate_text_lines(lines, target_lang))


def translate_text_file(input_file, output_file, target_lang="Korean"):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    translated_lines = translate_text_lines([l.strip() for l in lines if l.strip()], target_lang)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(translated_lines))

    print(f"Saved translated text file as {output_file}")


# --------------------------
# Master Pipeline
# --------------------------
def run_translation(mode, source, output=None, target_lang="Korean", max_slides=None):
    """
    mode = "pptx" | "text" | "file"
    source = input file (pptx or txt) OR raw text
    output = output file path (pptx or txt)
    """

    if mode == "pptx":
        if not output:
            raise ValueError("Output pptx path required.")
        translate_pptx(source, output, target_lang, max_slides)

    elif mode == "file":
        if not output:
            raise ValueError("Output text file path required.")
        translate_text_file(source, output, target_lang)

    elif mode == "text":
        result = translate_text_input(source, target_lang)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Saved translated text as {output}")
        else:
            print("Translated Text:\n", result)

    else:
        raise ValueError("Invalid mode. Choose from: pptx | file | text.")


# --------------------------
# Example Runs
# --------------------------
# PPTX example
run_translation("pptx", r"/content/P23_Research Data Analysis.pptx", "output_ko.pptx", target_lang="Korean", max_slides=12)

# Text example
# run_translation("text", "Hai", target_lang="Tamil")

# File example
# run_translation("file", "input.txt", "output_ta.txt", target_lang="Tamil")
