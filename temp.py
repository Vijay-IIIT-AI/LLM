docx_file = None  # Initialize docx_file before use

try:
    wordFile = confluence.get_page_as_word(page_id)
    temp_dir = tempfile.mkdtemp()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    doc_file = os.path.join(temp_dir, f"{page_id}_{timestamp}.doc")
    
    # Write the Word file to disk
    with open(doc_file, 'wb') as f:
        f.write(wordFile)
    
    # Convert .doc to .docx
    docx_file = doc_file.replace('.doc', '.docx')
    convert_doc_to_docx(doc_file, docx_file, libreoffice_path)  # You already have this function
    
    # Process docx file (Extract text, handle tables)
    text = extract_text_from_docx(docx_file)  # Assuming this function exists

    # Add to result dictionary
    result_dict[page_id] = text

except Exception as e:
    print(f"Error processing {page_id}: {e}")
finally:
    # Cleanup temporary files
    if docx_file and os.path.exists(docx_file):
        os.remove(docx_file)
    if os.path.exists(doc_file):
        os.remove(doc_file)
    if 'temp_dir' in locals() and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
