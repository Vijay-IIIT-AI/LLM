# Split the text by spaces and count the words
rows_with_few_words = df[df["page_contents"].str.split().str.len() < 20]

# Step 2: Get the page_id of those rows
page_ids_to_remove = rows_with_few_words["page_id"].tolist()

# Step 3: Remove rows with fewer than 20 words
df = df[df["page_contents"].str.split().str.len() >= 20]
