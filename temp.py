import requests
import json
from requests.auth import HTTPBasicAuth


class Page:
    def _init_(self, title, url, page_id):
        self.url = url
        self.id = page_id
        self.title = title
        self.level = 0
        self.ancestors = []

    def _str_(self):
        return self.title + " - " + self.url


def get_pages(site, auth, space):
    headers = {"Content-Type": "application/json"}
    pages = []
    cql = f"space = {space} AND type = page"  # or blogpost
    url = f"{site}/rest/api/content/search?cql={cql}&start=0&limit=50&expand=ancestors"

    # Initial request
    r = requests.get(url, headers=headers, auth=auth, timeout=10)
    r.raise_for_status()
    page_list = r.json()["results"]
    for page in page_list:
        pages.append(page)

    is_next_page = True

    # Handle pagination
    while is_next_page:
        try:
            next_page = r.json()["_links"]["next"]
            url = f"{site}{next_page}"
            r = requests.get(url, headers=headers, auth=auth)
            r.raise_for_status()
            page_list = r.json()["results"]
            for page in page_list:
                pages.append(page)
        except KeyError:
            is_next_page = False

    return pages


def create_page_obj(page):
    title = page["title"]
    url = page["_links"]["webui"]
    page_id = page["id"]
    p = Page(title, url, page_id)
    return p


def sort_pages(page_objs):
    """
    Sort pages into hierarchical order based on levels and ancestors.
    """
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
    for page in page_objs:
        if page not in sorted_pages:
            sorted_pages.append(page)
    return sorted_pages


def build_hierarchy(pages):
    """
    Build a nested hierarchy of pages based on their levels and ancestors.
    """
    page_dict = {page.id: page for page in pages}
    hierarchy = []

    for page in pages:
        if page.level == 0:
            hierarchy.append(page)
        else:
            parent_id = page.ancestors[-1] if page.ancestors else None
            if parent_id and parent_id in page_dict:
                parent = page_dict[parent_id]
                if not hasattr(parent, "children"):
                    parent.children = []
                parent.children.append(page)

    return hierarchy


def serialize_page(page):
    """
    Serialize a Page object into a dictionary format suitable for JSON-like output.
    """
    data = {
        "title": page.title,
        "url": page.url,
        "id": page.id,
        "level": page.level,
    }
    if hasattr(page, "children"):
        data["children"] = [serialize_page(child) for child in page.children]
    return data


def create_hierarchy_audit(site, username, password, space):
    """
    Generate a nested page hierarchy for a Confluence space.
    """
    auth = HTTPBasicAuth(username, password)
    pages = get_pages(site, auth, space)
    page_objs = []
    for page in pages:
        pg = create_page_obj(page)
        page_objs.append(pg)
        pg.level = len(page["ancestors"])
        ancestors = page["ancestors"]
        pg.ancestors = [ancestor["id"] for ancestor in ancestors]

    sorted_pages = sort_pages(page_objs)
    hierarchy = build_hierarchy(sorted_pages)
    return [serialize_page(page) for page in hierarchy]


# Example usage:
site_url = "https://yoursite.atlassian.net"
username = "your_email@example.com"
password = "your_password"
space_key = "your_space_key"

page_hierarchy = create_hierarchy_audit(site_url, username, password, space_key)
print(json.dumps(page_hierarchy, indent=4))
