from atlassian import Confluence
import camelot
import pandas as pd

# Confluence credentials
username = "<YOUR_USERNAME>"
password = "<YOUR_PASSWORD>"
url = "<YOUR_CONFLUENCE_URL>"

# Page ID and output file
page_id = "<YOUR_PAGE_ID>"
pdf_file = "confluence_page.pdf"

# Initialize Confluence API client
confluence = Confluence(
    url=url,
    username=username,
    password=password
)

# Fetch and save PDF
def fetch_pdf():
    try:
        response = confluence.get_page_as_pdf(page_id)
        with open(pdf_file, "wb") as file:
            file.write(response)
        print(f"PDF downloaded: {pdf_file}")
    except Exception as e:
        print(f"Error fetching PDF: {e}")

# Extract tables using Camelot
def extract_tables():
    try:
        tables = camelot.read_pdf(pdf_file, pages="all", flavor="stream")
        print(f"Found {len(tables)} tables in the PDF.")

        # Process each table
        all_tables = []
        for i, table in enumerate(tables):
            df = table.df  # Table as DataFrame
            table_string = df.to_string(index=False, header=False)  # Convert DataFrame to string
            all_tables.append(f"Start Table {i + 1}\n{table_string}\nEnd Table {i + 1}")

        # Combine all table strings
        result = "\n\n".join(all_tables)
        print(result)
        return result
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return None

# Main function
def main():
    # Step 1: Fetch the PDF
    fetch_pdf()

    # Step 2: Extract tables
    table_data = extract_tables()
    if table_data:
        # Save the table data to a text file if needed
        with open("extracted_tables.txt", "w") as file:
            file.write(table_data)
        print("Extracted table data saved to 'extracted_tables.txt'.")

if __name__ == "__main__":
    main()
