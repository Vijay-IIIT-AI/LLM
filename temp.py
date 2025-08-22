from flask import Flask, request, jsonify
import tempfile
import os
import uuid
from minio import Minio, S3Error
from datetime import timedelta
from pptx import Presentation
import requests
import time
import re
import logging


#https://dl.min.io/client/mc/release/windows-amd64/mc.exe
# mc alias set myminio http://127.0.0.1:9000 minioadmin minioadmin
# mc ilm add myminio/translate --expiry-days 1
#https://dl.min.io/server/minio/release/windows-amd64/minio.exe
#.\minio.exe server C:\minio\data

# ==========================
# Setup Logging
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ==========================
# Translation Core
# ==========================
api_key = "mjLoMvjl6nnvofomLxPNDMWZsvuouvCz"

def is_url(text: str) -> bool:
    return bool(re.match(r"https?://\S+", text.strip()))

def is_symbolic(text: str) -> bool:
    if not text.strip():
        return True
    non_alpha_ratio = sum(1 for c in text if not c.isalpha()) / len(text)
    return non_alpha_ratio > 0.7 or len(text) <= 3

def translate(text: str, tgt: str = "Korean") -> str:
    if not text.strip() or is_url(text) or is_symbolic(text):
        return text

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": f"Translate strictly into {tgt}. Only return translated text."},
            {"role": "user", "content": text}
        ]
    }

    try:
        time.sleep(0.3)
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        logging.error("Translation request timed out.")
        return text
    except requests.exceptions.RequestException as e:
        logging.error(f"Translation API error: {e}")
        return text
    except Exception as e:
        logging.error(f"Unexpected translation error: {e}")
        return text


# PPTX Translation
def translate_paragraph(para, target_lang="Korean"):
    for run in para.runs:
        run.text = translate(run.text, target_lang)

def translate_pptx(input_pptx, output_pptx, target_lang="Korean"):
    prs = Presentation(input_pptx)
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    translate_paragraph(para, target_lang)
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for para in cell.text_frame.paragraphs:
                            translate_paragraph(para, target_lang)
    prs.save(output_pptx)


# Text Translation
def translate_text_file(input_file, output_file, target_lang="Korean"):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"Error reading text file: {e}")
        raise

    translated = [translate(line, target_lang) for line in lines]

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(translated))


# ==========================
# Flask + MinIO API
# ==========================
app = Flask(__name__)

minio_client = Minio(
    "127.0.0.1:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
BUCKET_NAME = "translate"

# Ensure bucket exists
try:
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
except S3Error as e:
    logging.error(f"MinIO bucket error: {e}")


@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Unhandled exception occurred")
    return jsonify({"error": str(e)}), 500


@app.route("/translate", methods=["POST"])
def translate_endpoint():
    """
    Params:
      - mode = pptx | file
      - target_lang (default Korean)
      - file (uploaded file)
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    mode = request.form.get("mode", "pptx")
    target_lang = request.form.get("target_lang", "Korean")
    file = request.files["file"]

    # Assign unique name
    unique_id = str(uuid.uuid4())[:8]
    original_filename = file.filename or "uploaded_file"
    object_name = f"input/{unique_id}_{original_filename}"

    temp_files = []
    try:
        # Save uploaded file locally
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            local_input = tmp.name
            temp_files.append(local_input)

        # Upload to MinIO
        minio_client.fput_object(BUCKET_NAME, object_name, local_input)
        logging.info(f"Uploaded original file to MinIO: {object_name}")

        # Prepare translated file
        ext = ".pptx" if mode == "pptx" else ".txt"
        local_output = local_input + "_translated" + ext
        translated_object = f"output/{unique_id}_{original_filename.rsplit('.',1)[0]}_translated{ext}"
        temp_files.append(local_output)

        # Run translation
        if mode == "pptx":
            translate_pptx(local_input, local_output, target_lang)
        elif mode == "file":
            translate_text_file(local_input, local_output, target_lang)
        else:
            return jsonify({"error": "Invalid mode, choose pptx or file"}), 400

        # Upload translated file
        minio_client.fput_object(BUCKET_NAME, translated_object, local_output)
        logging.info(f"Uploaded translated file to MinIO: {translated_object}")

        # Generate presigned URL
        url = minio_client.presigned_get_object(
            BUCKET_NAME, translated_object, expires=timedelta(hours=1)
        )

        return jsonify({
            "status": "success",
            "mode": mode,
            "target_lang": target_lang,
            "translated_file": translated_object,
            "download_url": url
        })

    except S3Error as e:
        logging.error(f"MinIO error: {e}")
        return jsonify({"error": "File storage failed"}), 500
    except Exception as e:
        logging.error(f"Translation pipeline error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup temp files
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as cleanup_err:
                logging.warning(f"Temp file cleanup failed: {cleanup_err}")


@app.route("/stats", methods=["GET"])
def stats():
    try:
        total_files = 0
        total_size = 0
        objects_info = []

        # Iterate all objects in the bucket
        for obj in minio_client.list_objects(BUCKET_NAME, recursive=True):
            total_files += 1
            total_size += obj.size
            objects_info.append({
                "name": obj.object_name,
                "size_bytes": obj.size,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None
            })

        return jsonify({
            "bucket": BUCKET_NAME,
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "objects": objects_info
        })

    except S3Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=False)  # disable debug in production
