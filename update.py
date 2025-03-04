import os
import platform
import subprocess
import pandas as pd
from PIL import Image
from pdf2image import convert_from_path
import base64

def get_system_type():
    return platform.system().lower()

def check_office_availability():
    system_type = get_system_type()
    if system_type == "linux":
        try:
            subprocess.run(["libreoffice", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except FileNotFoundError:
            return False
    return False

def convert_ppt_to_pdf_linux(pptfile_name, out_dir):
    pdf_path = os.path.join(out_dir, os.path.splitext(os.path.basename(pptfile_name))[0] + ".pdf")
    command = ["soffice", "--headless", "--convert-to", "pdf", "--outdir", out_dir, pptfile_name]
    subprocess.run(command, check=True)
    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF conversion failed.")
    return pdf_path

def convert_pdf_to_images_linux(pdf_path, out_dir, img_format="png"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    images = convert_from_path(pdf_path, dpi=300, fmt=img_format)
    image_paths = []
    for i, image in enumerate(images):
        img_path = os.path.join(out_dir, f"slide_{i+1}.{img_format}")
        image.save(img_path, img_format.upper())
        image_paths.append(img_path)
    if not image_paths:
        raise RuntimeError("Image extraction failed.")
    return image_paths

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def extract_ppt_slides(pptx_path, output_folder):
    if not pptx_path.endswith(".pptx"):
        raise ValueError("Invalid file format. Only .pptx files are allowed.")

    system_type = get_system_type()
    pptx_filename = os.path.basename(pptx_path).split('.')[0]
    ppt_output_folder = os.path.join(output_folder, f"{pptx_filename}_ppt_image_extracted")
    os.makedirs(ppt_output_folder, exist_ok=True)
    slides_folder = os.path.join(ppt_output_folder, "slides")
    os.makedirs(slides_folder, exist_ok=True)
    csv_data = []
    pdf_path = None

    if check_office_availability():
        pdf_path = convert_ppt_to_pdf_linux(pptx_path, ppt_output_folder)
        images = convert_pdf_to_images_linux(pdf_path, slides_folder)
    else:
        raise RuntimeError("LibreOffice not found! Cannot process PPTX file.")

    for i, img_path in enumerate(images):
        base64_data = encode_image_to_base64(img_path)
        csv_data.append([i+1, pptx_filename, base64_data])

    df = pd.DataFrame(csv_data, columns=["SlideNumber", "FileName", "Base64Data"])
    csv_path = os.path.join(ppt_output_folder, "slide_mapping.csv")
    df.to_csv(csv_path, index=False)
    print(f"Slides extracted successfully to {ppt_output_folder}")

    return df

conda config --set proxy_servers.http http://user:password@proxyIP:proxyPort/
conda config --set proxy_servers.https http://user:password@proxyIP:proxyPort/
conda config --show | findstr "proxy"

