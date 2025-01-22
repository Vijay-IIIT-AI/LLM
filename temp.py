import requests
import json

# Replace with your actual token and site information
token = "your_super_secret_token"
site = "https://yoursite.atlassian.com"

class Page:
    def __init__(self, title, url, page_id):
        self.url = url
        self.id = page_id
        self.title = title
        self.level = 0
        self.ancestors = []

    def __str__(self):
        return self.title + ' - ' + self.url


def get_pages(space):
    headers = {
        "Authorization": "Basic " + token,
        "Content-Type": "application/json"
    }

    pages = []
    cql = f'space = {space} AND type = page'
    url = site + f'/rest/api/content/search?cql={cql}&start=0&limit=50&expand=ancestors'

    # Initial request to get pages
    r = requests.get(url, headers=headers, timeout=10)
    page_list = r.json().get('results', [])
    pages.extend(page_list)

    # Pagination to fetch all pages
    while '_links' in r.json() and 'next' in r.json()['_links']:
        next_page = r.json()['_links']['next']
        url = site + next_page
        r = requests.get(url, headers=headers, timeout=10)
        pages.extend(r.json().get('results', []))

    return pages


def create_page_obj(page):
    title = page['title']
    url = page['_links']['webui']
    page_id = page["id"]
    p = Page(title, url, page_id)
    return p


def sort_pages(page_objs):
    sorted_pages = []
    page_levels = max(page.level for page in page_objs)
    for level in range(page_levels + 1):
        if level == 0:
            sorted_pages.extend([page for page in page_objs if page.level == 0])
        else:
            children = [page for page in page_objs if page.level == level]
            parents = [page for page in sorted_pages if page.level == level - 1]
            for page in children:
                for parent in parents:
                    if parent.id in page.ancestors:
                        sorted_pages.insert(sorted_pages.index(parent) + 1, page)
                        break
    return sorted_pages


def create_hierarchy_audit_json(space):
    pages = get_pages(space)
    page_objs = []

    for page in pages:
        pg = create_page_obj(page)
        pg.level = len(page.get('ancestors', []))
        pg.ancestors = [ancestor['id'] for ancestor in page.get('ancestors', [])]
        page_objs.append(pg)

    sorted_pages = sort_pages(page_objs)

    hierarchy = []
    for page in sorted_pages:
        link = site + page.url
        hierarchy.append({
            "Tree depth": page.level,
            "Title": page.title,
            "URL": link
        })

    with open(f'./{space}_hierarchy.json', 'w') as json_file:
        json.dump(hierarchy, json_file, indent=4)

    return hierarchy

# Example usage
space = "YOUR_SPACE_KEY"
create_hierarchy_audit_json(space)
