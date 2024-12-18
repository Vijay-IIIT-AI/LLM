import requests
from bs4 import BeautifulSoup

# Configuration variables
BASE_URL = "https://your-confluence-instance.atlassian.net/wiki/rest/api/content/"
EMAIL = "your-email@example.com"
API_TOKEN = "your-api-token"


# Fetch page HTML content from Confluence
def fetch_page_as_html(page_id):
    url = f"{BASE_URL}{page_id}?expand=body.export_view"
    response = requests.get(url, auth=(EMAIL, API_TOKEN))

    if response.status_code == 200:
        content = response.json()
        html_content = content['body']['export_view']['value']
        return html_content
    else:
        print(f"Failed to fetch page {page_id}: {response.status_code}, {response.text}")
        return None

# Process the HTML to extract text and format tables
def process_html(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract all text, preserving table order
        result_text = []
        
        for element in soup.descendants:
            if element.name == "table":  # Handle tables
                table_text = []
                rows = element.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    cell_text = [cell.get_text(strip=True) for cell in cells]
                    table_text.append("\t".join(cell_text))
                formatted_table = f"[START][TABLE]\n{'\n'.join(table_text)}\n[END][TABLE]"
                result_text.append(formatted_table)
            elif element.name in ["p", "div", "span"]:  # Handle text elements
                text = element.get_text(strip=True)
                if text:
                    result_text.append(text)

        return "\n\n".join(result_text)
    except Exception as e:
        print(f"Error processing HTML: {e}")
        return None

# Main function to handle multiple Page IDs
def process_page_ids(page_ids):
    result = {}
    for page_id in page_ids:
        print(f"Processing page ID: {page_id}")

        # Fetch HTML content
        html_content = fetch_page_as_html(page_id)
        if not html_content:
            print(f"Skipping page ID {page_id} due to fetch error.")
            continue

        # Process HTML and extract content
        formatted_content = process_html(html_content)
        if formatted_content:
            result[page_id] = formatted_content
        else:
            print(f"Failed to process content for page ID {page_id}.")

    return result

# Example usage
if __name__ == "__main__":
    PAGE_IDS = ["12345", "67890"]  # Replace with your page IDs

    content_map = process_page_ids(PAGE_IDS)

    # Display results
    if content_map:
        import json
        print(json.dumps(content_map, indent=4, ensure_ascii=False))
    else:
        print("No content was processed.")
