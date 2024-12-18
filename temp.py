import os
import shutil
import camelot
import tempfile
import concurrent.futures
from atlassian import Confluence
from datetime import datetime

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
            all_tables.append(f"[START[TABLE] Table {i + 1}]\n{table_string}\n[END[TABLE]]")

        # Combine all table strings into one result
        result = "\n\n".join(all_tables)
        return result
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return None

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
        page_content = table_data if table_data else "No tables found."

        # Step 3: Add page content to the result dictionary
        result_dict[page_id] = page_content

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

# Main function
def main(page_ids: list):
    # Create a temporary directory to store PDFs
    temp_dir = tempfile.mkdtemp()

    # Step 1: Process all pages (with or without batching)
    result_dict = process_pages_in_batches(page_ids, temp_dir)

    # Step 2: Optionally, save results to a text file or return them
    if result_dict:
        with open("page_contents.txt", "w") as file:
            for page_id, content in result_dict.items():
                file.write(f"{page_id}: {content}\n\n")
        print("Page contents saved to 'page_contents.txt'.")

    # Step 3: Cleanup the temporary directory
    cleanup_temp_directory(temp_dir)

# Example usage with a list of 100 page IDs
page_ids = [f"id_{i}" for i in range(1, 101)]  # Replace with your actual list of page IDs
main(page_ids)
