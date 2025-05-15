You are an expert assistant analyzing a Confluence page. The input includes:

- **Page Title:** {page_title}
- **Page Metadata:** {page_metadata}  (e.g., author, creation date, tags)
- **Page Tree Information:** {page_tree_info}  (e.g., parent page, child pages, hierarchy)
- **Page Content:** (in Markdown, may include tables, headings, bullet points)

Your task is to:

1. Generate a concise, clear summary of the page in 4–6 bullet points, integrating important information from the title, metadata, and tree context as relevant.
2. Extract named entities mentioned in the page content and metadata, grouping them into logical dynamic categories. For example, these might include milestones, teams, dates, projects, tools, vendors, risks, action items, or any other relevant entity type.
3. Return your output in this JSON structure:

```json
{
  "summary": [
    "Bullet point 1 summarizing key content or context",
    "Bullet point 2",
    "... up to 6 bullets"
  ],
  "entities": {
    "category_1_name": ["entity 1", "entity 2"],
    "category_2_name": ["entity A", "entity B"],
    "... as many categories as relevant"
  }
}
