import requests
import json

def get_confluence_page_tree(base_url, username, password, space_key):
    """
    Generates a JSON representation of the page tree for a given Confluence space.

    Args:
        base_url (str): The base URL of the Confluence instance (e.g., https://your-instance.atlassian.net/wiki).
        username (str): The Confluence username or email.
        password (str): The Confluence API token or password.
        space_key (str): The key of the Confluence space.

    Returns:
        dict: A JSON object representing the page tree.
    """
    def fetch_page_children(parent_id):
        """
        Fetches child pages for a given parent page ID.

        Args:
            parent_id (str): The ID of the parent page.

        Returns:
            list: A list of child pages represented as dictionaries.
        """
        url = f"{base_url}/rest/api/content/{parent_id}/child/page"
        params = {
            "expand": "title,children.page",
            "limit": 100
        }
        response = requests.get(url, auth=(username, password), params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch children for page {parent_id}: {response.status_code} {response.text}")

        data = response.json()
        children = []
        for child in data.get("results", []):
            children.append({
                "id": child["id"],
                "title": child["title"],
                "children": fetch_page_children(child["id"])
            })
        return children

    def build_tree():
        """
        Builds the page tree starting from the root pages of the space.

        Returns:
            list: A list of root pages represented as dictionaries.
        """
        url = f"{base_url}/rest/api/content"
        params = {
            "spaceKey": space_key,
            "type": "page",
            "expand": "title",
            "limit": 100,
            "ancestors": ""
        }
        response = requests.get(url, auth=(username, password), params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch root pages for space {space_key}: {response.status_code} {response.text}")

        data = response.json()
        root_pages = []
        for page in data.get("results", []):
            root_pages.append({
                "id": page["id"],
                "title": page["title"],
                "children": fetch_page_children(page["id"])
            })
        return root_pages

    try:
        return build_tree()
    except Exception as e:
        print(f"Error generating page tree: {e}")
        return None

# Example usage:
if _name_ == "_main_":
    confluence_url = "https://your-instance.atlassian.net/wiki"
    username = "your-email@example.com"
    password = "your-api-token"
    space_key = "YOURSPACE"

    page_tree = get_confluence_page_tree(confluence_url, username, password, space_key)

    if page_tree:
        print(json.dumps(page_tree, indent=2))
