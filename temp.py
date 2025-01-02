import pandas as pd

# Sample data for demonstration
Re_scarpeddict = {
    "page1": "Content from rescraped data for page 1",
    "page2": "Content from rescraped data for page 2",
    "page3": "Content from rescraped data for page 3"
}

markdowndata = {
    "page1": "Content from markdown data for page 1",
    "page2": "Content from markdown data for page 2",
    "page3": "Content from markdown data for page 3"
}

# Create a sample DataFrame
data = {
    'Page_content': [None, None, None],
    'page_id': ['page1', 'page2', 'page3'],
    'bool': [False, True, False]
}

df = pd.DataFrame(data)

# Function to map page content based on the bool value
def map_page_content(row):
    if row['bool']:
        return Re_scarpeddict.get(row['page_id'], None)
    else:
        return markdowndata.get(row['page_id'], None)

# Apply the function to the DataFrame
df['Page_content'] = df.apply(map_page_content, axis=1)

# Display the updated DataFrame
print(df)
