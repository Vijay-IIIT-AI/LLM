import re
import pandas as pd

# Sample complex Markdown input
markdown_text = """
This section contains the current progress.

 Phase               | Nov | Dec | Jan | Feb | Mar | Apr | May 
 Design Approval     | X   |     |     |     |     |     |     
 Development Phase   |     | X   | X   |     |     |     |     
 Integration Testing |     |     |     | X   |     |     |     
 Beta Release        |     |     |     |     | X   |     |     
 Final Release       |     |     |     |     |     |     | X    

---

### Budget Overview

 Budget Category      | Allocated Amount (USD) | Spent Amount (USD) | % Utilized | Comments  
 ---|---|---|---|---                      
 Development          | 200,000               | 125,000             | 62.5%      | Majority spent on dev tools.   
 Marketing            | 50,000                | 20,000              | 40%        | Initial campaign costs covered.
 QA and Testing       | 30,000                | 5,000               | 16.7%      | Reserved for integration phase.
 Contingency          | 20,000                | 0                   | 0%         | No emergencies to date.         

Some additional context about the budget and its implications.
# Project Milestones & Progress

The following table shows the current milestones in our project timeline.

| Milestone              | Due Date       | Status        | Responsible Team    | Comments                              |
|------------------------|----------------|---------------|---------------------|---------------------------------------|
| Design Approval        | 2024-11-30     | Completed     | UX/UI Team          | Final designs approved by stakeholders. |
| Development Phase 1    | 2024-12-31     | In Progress   | Frontend, Backend   | Frontend development 60% complete. Backend API setup initiated. |
| Integration Testing    | 2025-02-15     | Not Started   | QA Team             | Scheduled to begin post-development. |
| Beta Release           | 2025-03-01     | Not Started   | Release Team        | Beta testers recruitment ongoing. |
| Final Release          | 2025-05-01     | On Track      | All Teams           | Pending completion of integration testing. |

---

## Budget Overview

This section provides details about the current budget allocation and expenditures.

| Budget Category        | Allocated Amount (USD) | Spent Amount (USD) | % Utilized | Comments                                |
|------------------------|------------------------|--------------------|------------|-----------------------------------------|
| Development            | 200,000               | 125,000             | 62.5%      | Majority spent on dev tools.           |
| Marketing              | 50,000                | 20,000              | 40%        | Initial campaign costs covered.        |
| QA and Testing         | 30,000                | 5,000               | 16.7%      | Reserved for integration phase.        |
| Contingency            | 20,000                | 0                   | 0%         | No emergencies to date.                |

Some additional context about the budget and its implications. The marketing team has not yet utilized the full allocated budget, with most expenditures focused on initial campaigns and planning for future promotions.

---

### Future Milestones

We will begin planning for the next quarter’s objectives after the Beta Release phase. These will be the key milestones:

1. **Final Testing**: Final testing before the full product release.
2. **Product Documentation**: Documentation will be drafted and finalized.
3. **Customer Support Setup**: Setting up customer support channels for post-launch queries.

---

### Key Risks & Contingency Plans

While we have made significant progress, there are a few key risks to monitor:

- **Resource Availability**: A few team members may be unavailable due to holidays in December.
- **Market Conditions**: Changes in market conditions could affect the marketing budget.

We have allocated contingency funds to mitigate these risks and ensure smooth progress through the next phases.

---

Some additional context here about the upcoming phases and general project overview.

"""

# Function to chunk Markdown text
def chunk_markdown_with_tables(text, max_words=200, table_context=3):
    # Split the text into lines
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    in_table = False
    table_start = -1
    table_end = -1

    def add_chunk(chunk_lines):
        """Add a new chunk if it contains content."""
        chunk = "\n".join(chunk_lines).strip()
        if chunk:
            chunks.append(chunk)

    for i, line in enumerate(lines):
        # Detect the start of a table
        if "|" in line and not re.match(r"^\s*-+\s*$", line):
            if not in_table:
                # Add pre-table context (up to `table_context` lines)
                table_start = i
                pre_context_start = max(0, table_start - table_context)
                current_chunk.extend(lines[pre_context_start:table_start])
                in_table = True
            current_chunk.append(line)
        elif in_table:
            # Add table lines and detect end of the table
            if "|" in line or not line.strip():
                current_chunk.append(line)
            else:
                # Add post-table context (up to `table_context` lines)
                table_end = i
                post_context_end = min(len(lines), table_end + table_context)
                current_chunk.extend(lines[table_end:post_context_end])
                add_chunk(current_chunk)
                current_chunk = []
                in_table = False
        else:
            # Regular text, add to the chunk
            current_chunk.append(line)

        # Chunk based on word count
        if not in_table and len(" ".join(current_chunk).split()) >= max_words:
            add_chunk(current_chunk)
            current_chunk = []

    # Add the last chunk
    add_chunk(current_chunk)

    return chunks

# Process the input text
chunks = chunk_markdown_with_tables(markdown_text)

# Convert chunks into a DataFrame for enriched output
df = pd.DataFrame({
    "Enriched_Page_Content": chunks,
    "Meta_Data": ["Auto-generated"] * len(chunks),  # Placeholder for meta-data
    "Page_ID": range(1, len(chunks) + 1)  # Auto-incremental page IDs
})

# Display the result
print(df)

# Save the DataFrame to a CSV file (optional)
df.to_csv("enriched_chunks.csv", index=False)
