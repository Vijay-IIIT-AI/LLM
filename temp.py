import pandas as pd

# Example dataframe
data = {
    "info": [True, False, True, False],
    "page_content": ["Content1", "Content2", "Content3", "Content4"],
    "page_id": [101, 102, 103, 104],
}
df = pd.DataFrame(data)

# Step 1: Get the list of `page_id` where `info` is True
page_ids = df.loc[df["info"], "page_id"].tolist()

# Step 2: Define a function to get updated content (simulate the function call)
def get_updated_contents(page_ids):
    # Example dictionary returned by the function
    return {101: "Updated Content1", 103: "Updated Content3"}

updated_contents = get_updated_contents(page_ids)

# Step 3: Update `page_content` in the dataframe
df["page_content"] = df.apply(
    lambda row: updated_contents[row["page_id"]] if row["page_id"] in updated_contents else row["page_content"],
    axis=1
)

print(df)
