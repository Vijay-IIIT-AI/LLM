import requests
import html2text
import re

def fetch_html_content(page_id, base_url, username, password):
    """
    Fetches HTML content from the Confluence page using its API.
    
    Args:
        page_id (str): The ID of the Confluence page.
        base_url (str): The base URL of the Confluence instance.
        username (str): Username for Confluence authentication.
        password (str): Password or API token for Confluence authentication.
    
    Returns:
        str: The HTML content of the page.
    """
    api_url = f"{base_url}/wiki/rest/api/content/{page_id}?expand=body.export_view"
    try:
        response = requests.get(api_url, auth=(username, password))
        response.raise_for_status()
        return response.json()["body"]["export_view"]["value"]
    except requests.RequestException as e:
        print(f"Failed to fetch HTML content for page ID {page_id}: {e}")
        return None

def clean_text(text):
    """
    Cleans the text content by removing unwanted characters like emojis and special symbols.
    
    Args:
        text (str): The plain text to be cleaned.
    
    Returns:
        str: Cleaned text.
    """
    # Remove emojis and non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Remove extra spaces and unwanted newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def convert_html_to_text(html_content):
    """
    Converts HTML content into plain text using the html2text library.
    
    Args:
        html_content (str): The HTML content to convert.
    
    Returns:
        str: The plain text content.
    """
    if not html_content:
        return ""
    
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    plain_text = converter.handle(html_content)
    return clean_text(plain_text)

def fetch_and_process_pages(page_ids, base_url, username, password):
    """
    Fetches HTML content for each page ID, converts it to plain text, and returns a mapping.
    
    Args:
        page_ids (list): List of Confluence page IDs.
        base_url (str): The base URL of the Confluence instance.
        username (str): Username for Confluence authentication.
        password (str): Password or API token for Confluence authentication.
    
    Returns:
        dict: A dictionary mapping page IDs to their plain text content.
    """
    result = {}
    for page_id in page_ids:
        html_content = fetch_html_content(page_id, base_url, username, password)
        plain_text = convert_html_to_text(html_content)
        result[page_id] = plain_text
    return result

def main():
    # Variables to be provided
    page_ids = ["id_1", "id_2"]  # Replace with your list of Page IDs
    base_url = "https://your-confluence-host.com"  # Replace with your Confluence base URL
    username = "your-username"  # Replace with your username
    password = "your-password"  # Replace with your password or API token
    
    # Fetch and process pages
    page_contents = fetch_and_process_pages(page_ids, base_url, username, password)
    
    # Print the result
    for page_id, content in page_contents.items():
        print(f"Page ID: {page_id}\nContent:\n{content}\n")

if __name__ == "__main__":
    main()
