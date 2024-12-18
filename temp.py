import requests

# Constants
BASE_URL = "https://yourdomain.atlassian.net/wiki"
API_ENDPOINT = "/rest/api/content"
EMAIL = "your_email@example.com"
API_TOKEN = "your_api_token"

# Fetch page HTML export
def fetch_page_as_html(page_id):
    url = f"{BASE_URL}{API_ENDPOINT}/{page_id}?expand=body.export_view"
    response = requests.get(url, auth=(EMAIL, API_TOKEN))

    if response.status_code == 200:
        content = response.json()
        html_content = content['body']['export_view']['value']
        return html_content
    else:
        print(f"Failed to fetch page: {response.status_code}, {response.text}")
        return None

# Save HTML content to a file
def save_html_to_file(html_content, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

# Example usage
page_id = "123456"  # Replace with your page ID
html_content = fetch_page_as_html(page_id)

if html_content:
    save_html_to_file(html_content, "page.html")
    print("Page saved as page.html")
