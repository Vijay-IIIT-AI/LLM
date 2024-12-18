import requests
from requests.auth import HTTPBasicAuth

# Input variables
page_id = "<YOUR_PAGE_ID>"
username = "<YOUR_USERNAME>"
password = "<YOUR_PASSWORD>"
url = "<YOUR_CONFLUENCE_URL>"

# Construct the API endpoint
api_url = f"{url}/rest/api/content/{page_id}?expand=body.storage"

# Make the GET request
try:
    response = requests.get(api_url, auth=HTTPBasicAuth(username, password))

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the page content
        page_title = data.get("title", "No Title")
        page_content = data.get("body", {}).get("storage", {}).get("value", "No Content")
        
        print(f"Page Title: {page_title}")
        print(f"Page Content:\n{page_content}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")
