import requests
import json


class Page:
    def __init__(self, title, url, page_id):
        self.url = url
        self.id = page_id
        self.title = title
        self.level = 0
        self.ancestors = []

    def __str__(self):
        return self.title + ' - ' + self.url


def get_pages(space_key, server_url, auth):
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }

    pages = []
    cql = f'space = {space_key} AND type = page'
    url = f'{server_url}/rest/api/content/search?cql={cql}&start=0&limit=50&expand=ancestors'

    # Get the initial list of pages
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    page_list = r.json()['results']
    pages.extend(page_list)

    # Handle pagination to get all pages
    while '_links' in r.json() and 'next' in r.json()['_links']:
        next_page = r.json()['_links']['next']
        url = f'{server_url}{next_page}'
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        page_list = r.json()['results']
        pages.extend(page_list)

    return pages


def create_page_obj(page):
    title = page['title']
    url = page['_links']['webui']
    page_id = page["id"]
    p = Page(title, url, page_id)
    return p


def build_page_tree(pages):
    page_map = {page.id: page for page in pages}
    root_pages = [page for page in pages if not page.ancestors]

    def build_tree(page):
        children = [child for child in pages if page.id in child.ancestors]
        return {
            "title": page.title,
            "url": page.url,
            "children": [build_tree(child) for child in children]
        }

    tree = [build_tree(root) for root in root_pages]
    return tree


def create_page_tree_json(space_key, server_url, username, password):
    # Encode username and password for basic authentication
    auth = requests.auth._basic_auth_str(username, password)
    raw_pages = get_pages(space_key, server_url, auth)

    page_objs = []
    for page in raw_pages:
        pg = create_page_obj(page)
        pg.level = len(page['ancestors'])
        pg.ancestors = [ancestor['id'] for ancestor in page['ancestors']]
        page_objs.append(pg)

    page_tree = build_page_tree(page_objs)
    # Write the JSON tree to a file
    with open(f'{space_key}_page_tree.json', 'w') as f:
        json.dump(page_tree, f, indent=4)
    return page_tree


# Example usage
if __name__ == "__main__":
    server_url = "https://yoursite.atlassian.net"
    space_key = "YOUR_SPACE_KEY"
    username = "your_username"
    password = "your_password"

    page_tree = create_page_tree_json(space_key, server_url, username, password)
    print(json.dumps(page_tree, indent=4))
