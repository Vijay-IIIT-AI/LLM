import os
import shutil
import camelot
import tempfile
import concurrent.futures
from atlassian import Confluence
from datetime import datetime
import json

# Setup Confluence connection (use your credentials here)
confluence = Confluence(url='your_confluence_url', username='your_username', password='your_password')

# Function to fetch and save PDF from Confluence page
def fetch_pdf(page_id: str, pdf_file: str):
    try:
        response = confluence.get_page_as_pdf(page_id)
        with open(pdf_file, "wb") as file:
            file.write(response)
        print(f"PDF downloaded: {pdf_file}")
    except Exception as e:
        print(f"Error fetching PDF for {page_id}: {e}")

# Function to extract tables using Camelot from the PDF
def extract_tables(pdf_file: str):
    try:
        # Using camelot to extract tables from the PDF
        tables = camelot.read_pdf(pdf_file, pages="all", flavor="stream")
        print(f"Found {len(tables)} tables in the PDF.")

        # Process each table and convert it into string format
        all_tables = []
        for i, table in enumerate(tables):
            df = table.df  # Convert table to DataFrame
            table_string = df.to_string(index=False, header=False)  # Convert DataFrame to string
            all_tables.append(f"[START][TABLE]\n{table_string}\n[END][TABLE]")

        return all_tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

# Function to extract text content from the PDF
def extract_text(pdf_file: str):
    try:
        # Extract text from the PDF using PyPDF2 or any other library
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_file)
        text_content = ""
        
        for page in reader.pages:
            text_content += page.extract_text()

        return text_content
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

# Function to process a single page ID
def process_single_page(page_id: str, temp_dir: str):
    result_dict = {}
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_file = os.path.join(temp_dir, f"{page_id}_{timestamp}.pdf")

        # Step 1: Fetch the PDF
        fetch_pdf(page_id, pdf_file)

        # Step 2: Extract tables from the PDF
        table_data = extract_tables(pdf_file)

        # Step 3: Extract text content from the PDF
        text_content = extract_text(pdf_file)

        # Combine text and table data while maintaining order
        combined_content = text_content
        if table_data:
            # Add the tables after the relevant content
            combined_content += "\n\n".join(table_data)

        # Step 4: Add page content to the result dictionary
        result_dict[page_id] = combined_content

    except Exception as e:
        print(f"Error processing page {page_id}: {e}")
        
    finally:
        # Cleanup - Remove the temporary PDF file after processing
        if os.path.exists(pdf_file):
            os.remove(pdf_file)

    return result_dict

# Function to handle multiple pages in batches with parallel processing
def process_pages_in_batches(page_ids: list, temp_dir: str, batch_size: int = 10):
    all_results = {}
    # Create temporary directory if not exists
    os.makedirs(temp_dir, exist_ok=True)

    # Split page IDs into batches only if there are more than 'batch_size' page_ids
    if len(page_ids) > batch_size:
        # Split page IDs into batches
        for i in range(0, len(page_ids), batch_size):
            batch = page_ids[i:i + batch_size]
            
            # Use ThreadPoolExecutor to process pages in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_page = {executor.submit(process_single_page, page_id, temp_dir): page_id for page_id in batch}
                
                for future in concurrent.futures.as_completed(future_to_page):
                    page_id = future_to_page[future]
                    try:
                        result = future.result()
                        all_results.update(result)  # Merge results from each page
                    except Exception as e:
                        print(f"Error while processing {page_id}: {e}")
    else:
        # If there are fewer than 'batch_size' page IDs, process sequentially
        for page_id in page_ids:
            result_dict = process_single_page(page_id, temp_dir)
            all_results.update(result_dict)

    return all_results

# Function to delete temp directory
def cleanup_temp_directory(temp_dir: str):
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Temporary directory {temp_dir} cleaned up.")

# Function to save the result dictionary as JSON
def save_results_as_json(result_dict: dict, json_file: str):
    try:
        with open(json_file, "w") as json_file:
            json.dump(result_dict, json_file, indent=4)
        print(f"Results saved to {json_file}")
    except Exception as e:
        print(f"Error saving results to JSON: {e}")

# Main function
def main(page_ids: list):
    # Create a temporary directory to store PDFs
    temp_dir = tempfile.mkdtemp()

    # Step 1: Process all pages (with or without batching)
    result_dict = process_pages_in_batches(page_ids, temp_dir)

    # Step 2: Save the results to a JSON file
    if result_dict:
        save_results_as_json(result_dict, "page_contents.json")

    # Step 3: Cleanup the temporary directory
    cleanup_temp_directory(temp_dir)

# Example usage with a list of 100 page IDs
page_ids = [f"id_{i}" for i in range(1, 101)]  # Replace with your actual list of page IDs
main(page_ids)
