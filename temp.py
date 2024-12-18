import os
import subprocess
import time
import docx
import shutil
from datetime import datetime
from typing import List, Dict
from atlassian import Confluence

# Function to check if LibreOffice is installed
def check_libreoffice_installed(libreoffice_path: str):
    try:
        subprocess.run([libreoffice_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        raise EnvironmentError(f"LibreOffice is not installed or not accessible from {libreoffice_path}")

# Function to convert .doc to .docx
def convert_doc_to_docx(doc_file: str, docx_file: str, libreoffice_path: str):
    # Check if LibreOffice is installed
    check_libreoffice_installed(libreoffice_path)
    
    # Convert the doc file to docx using LibreOffice
    command = f'{libreoffice_path} --headless --convert-to docx "{doc_file}" --outdir "{os.path.dirname(docx_file)}"'
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error during document conversion: {e}")

# Function to extract text content from a docx file (handling tables)
def extract_text_from_docx(docx_file: str) -> str:
    doc = docx.Document(docx_file)
    text_content = ""
    
    for para in doc.paragraphs:
        text_content += para.text + "\n"
    
    # Detect and process tables
    for table in doc.tables:
        text_content += "\n[START[TABLE]]\n"
        for row in table.rows:
            row_text = [cell.text for cell in row.cells]
            text_content += "\t".join(row_text) + "\n"
        text_content += "\n[END[TABLE]]\n"

    return text_content.strip()

# Function to create a temp directory for storing the files
def create_temp_dir(base_path: str, page_id: str) -> str:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_dir = os.path.join(base_path, f"temp_{page_id}_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

# Function to delete the temp directory and the generated docx file
def clean_up(temp_dir: str, docx_file: str):
    if os.path.exists(docx_file):
        os.remove(docx_file)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Function to get page as Word (.doc) from Confluence using Atlassian Python API
def get_page_as_word(confluence_instance: Confluence, page_id: str) -> bytes:
    """
    Downloads a page from Confluence as a Word file (.doc).
    
    Args:
        confluence_instance (Confluence): The Confluence instance for interacting with the API.
        page_id (str): The ID of the Confluence page.
        
    Returns:
        bytes: The Word file content.
    """
    try:
        # Fetch the Word export of the page
        word_file = confluence_instance.get_page_as_word(page_id)
        return word_file
    except Exception as e:
        raise RuntimeError(f"Error fetching page {page_id}: {e}")

# Main function to handle the full process
def process_pages(page_ids: List[str], base_path: str, confluence_url: str, username: str, password: str, libreoffice_path: str) -> Dict[str, str]:
    # Create Confluence instance
    confluence_instance = Confluence(
        url=confluence_url,
        username=username,
        password=password
    )
    
    result_dict = {}
    
    for page_id in page_ids:
        temp_dir = create_temp_dir(base_path, page_id)
        try:
            # Step 1: Get the .doc file from Confluence
            word_file_content = get_page_as_word(confluence_instance, page_id)
            
            # Save the .doc file locally
            doc_file = os.path.join(temp_dir, f"{page_id}.doc")
            with open(doc_file, "wb") as f:
                f.write(word_file_content)
            
            # Step 2: Convert .doc to .docx
            docx_file = os.path.join(temp_dir, f"{page_id}.docx")
            convert_doc_to_docx(doc_file, docx_file, libreoffice_path)
            
            # Step 3: Extract text from docx
            text_content = extract_text_from_docx(docx_file)
            
            # Step 4: Store the content in the result dictionary
            result_dict[page_id] = text_content
        except Exception as e:
            print(f"Error processing {page_id}: {e}")
        finally:
            # Clean up the generated docx file and temp directory
            clean_up(temp_dir, docx_file)
    
    return result_dict

# Example usage
page_ids = ['id_1', 'id_2']
base_path = '/path/to/temp/folder'  # Pass this as a variable when calling the function
confluence_url = 'https://your-confluence-instance.com'  # Replace with your Confluence URL
username = 'your-username'  # Replace with your Confluence username
password = 'your-password'  # Replace with your Confluence password
libreoffice_path = os.getenv("LIBREOFFICE_PATH", "libreoffice")  # Set LibreOffice path dynamically

# Process the pages and get the content
content_dict = process_pages(page_ids, base_path, confluence_url, username, password, libreoffice_path)

# Print the content for each Page_ID
for page_id, content in content_dict.items():
    print(f"Page {page_id}: {content[:500]}...")  # Print first 500 chars for preview
