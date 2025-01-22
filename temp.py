def build_hierarchy(pages):
    page_dict = {page.id: {"title": page.title, "url": site + page.url, "children": []} for page in pages}
    root_pages = []

    for page in pages:
        if page.ancestors:
            parent_id = page.ancestors[-1]  # Get the immediate parent
            if parent_id in page_dict:
                page_dict[parent_id]["children"].append(page_dict[page.id])
        else:
            root_pages.append(page_dict[page.id])

    return root_pages

def create_hierarchy_audit_json(space):
    pages = get_pages(space)
    page_objs = []

    for page in pages:
        pg = create_page_obj(page)
        pg.level = len(page.get('ancestors', []))
        pg.ancestors = [ancestor['id'] for ancestor in page.get('ancestors', [])]
        page_objs.append(pg)

    sorted_pages = sort_pages(page_objs)
    hierarchy = build_hierarchy(sorted_pages)

    with open(f'./{space}_hierarchy.json', 'w') as json_file:
        json.dump(hierarchy, json_file, indent=4)

    return hierarchy
