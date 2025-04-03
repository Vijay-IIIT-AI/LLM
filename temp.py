def check_page_changes(new_pages, old_pages):
    added = [page for page in new_pages if page not in old_pages]
    deleted = [page for page in old_pages if page not in new_pages]

    if not added and not deleted:
        return "No change"
    
    return {"added": added, "deleted": deleted}

# Example usage
a = [1, 2, 3]  # New Pages
b = [1, 2]     # Old Pages

result = check_page_changes(a, b)
print(result)
