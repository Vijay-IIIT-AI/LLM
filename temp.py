import pandas as pd

# Example dataframe
data = {
    "name": ["data_psr_dynamic", "data 123 qr_12", "other_data qr_14", "psr_dynamic_test"],
    "page_id": [101, 102, 103, 104],
}
df = pd.DataFrame(data)

# List of values to search for
premove_page_name_with = ["psr_dynamic", "qr_12"]

# Step 1: Create a regex pattern from the list to match any of these values
pattern = "|".join(premove_page_name_with)

# Step 2: Find rows where `name` contains any of the values (case-insensitive match)
matched_rows = df[df["name"].str.contains(pattern, case=False, na=False)]

# Step 3: Get the `page_id` of the matched rows
matched_page_ids = matched_rows["page_id"].tolist()

# Step 4: Drop the matched rows from the dataframe
df = df[~df["name"].str.contains(pattern, case=False, na=False)]

print("Matched Page IDs:", matched_page_ids)
print("\nUpdated DataFrame:")
print(df)
