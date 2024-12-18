df["page_content"] = df.apply(
    lambda row: updated_contents[row["page_id"]] if row["page_id"] in updated_contents else row["page_content"],
    axis=1
)
