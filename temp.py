Your task is to:

---

### 1. Generate a RAG-friendly Summary

- Break the content into 8-10 bullet points.
- Each bullet should be self-contained and capture one meaningful unit of information (e.g., a decision, milestone, risk, team responsibility, or plan).
- Be specific — include names, numbers, dates, team names, and referenced tools or files etc..,
- Cover **all sections** of the document — including tables and appendices.
- The summary should be dense with details and support downstream retrieval.

---

### 2. Extract Named Entities (Dynamic Categories)

- Extract specific, meaningful entities mentioned across the content, metadata, and tree.
- Group them into dynamic, **logically inferred** categories.
- Examples: milestones, owners, dates, systems, risks, tools, decisions, external dependencies, documents, locations, statuses, etc.
- You must **not hardcode** categories — infer what makes sense from the content.
- Return only meaningful and non-redundant values.

---

### 3. Output Format

Respond in this exact JSON structure, replacing values with real content:

```json
{{
  "summary": [
    "Detailed bullet point 1",
    "Detailed bullet point 2",
    "... up to 8"
  ],
  "entities": {{
    "category_name_1": ["entity A", "entity B"],
    "category_name_2": ["entity X", "entity Y"]
  }}
}}
