# Step 3: Identify rows with fewer than 20 total words/characters
rows_with_few_words = df[df["word_count"] < 20]

# Step 4: Get the `page_id` of rows to remove
page_ids_to_remove = rows_with_few_words["page_id"].tolist()

# Step 5: Drop rows with fewer than 20 total words/characters
df = df[df["word_count"] >= 20].drop(columns=["word_count"])  # Remove helper column if not needed
