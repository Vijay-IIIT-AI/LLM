import pandas as pd

def create_csv(space, pages):
    page_levels = max(page.level for page in pages)
    
    # Prepare fieldnames
    fieldnames = [f'Tree depth {level}' for level in range(page_levels + 1)]
    fieldnames.append('URL')
    
    # Create a list to store row data
    rows = []
    
    for page in pages:
        link = site + page.url
        row_dict = {f'Tree depth {page.level}': page.title, 'URL': link}
        rows.append(row_dict)
    
    # Create a DataFrame from the rows
    df = pd.DataFrame(rows, columns=fieldnames)
    return df
