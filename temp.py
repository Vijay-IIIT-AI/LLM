def get_page_by_id(page_id):
    headers = {
        "Authorization": "Basic " + token,
        "Content-Type": "application/json"
    }
    url = f"{site}/rest/api/content/{page_id}?expand=title"
    r = requests.get(url, headers=headers)
    
    if r.status_code == 200:
        return r.json()  # This will return the full page data, including the title.
    else:
        print(f"Error retrieving page with ID {page_id}")
        return None
