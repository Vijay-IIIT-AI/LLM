import re

def process_multiple_tables_without_separator(page_text):
    """
    Process multiple Markdown tables without separator rows within a single page and convert them into structured text.

    Args:
        page_text (str): The input Markdown text containing tables without separators.

    Returns:
        str: The structured text summarizing the tables.
    """
    structured_output = []

    # Regex to match tables based on pipe structure
    table_regex = r"(.*?)(\|[^\n]+\|\n(?:\|[^\n]+\|\n?)*)"
    matches = re.findall(table_regex, page_text, flags=re.DOTALL)

    for match in matches:
        surrounding_text = match[0].strip()
        table_text = match[1].strip()

        # Process the table into structured text
        structured_table = convert_table_to_structured_text_without_separator(table_text)

        # Combine with surrounding text for context
        enriched_text = f"{surrounding_text}\n\n{structured_table}"
        structured_output.append(enriched_text)

    return "\n\n---\n\n".join(structured_output)

def convert_table_to_structured_text_without_separator(table_text):
    """
    Convert a single Markdown table (without separator rows) into structured text.

    Args:
        table_text (str): The Markdown table.

    Returns:
        str: Structured text summarizing the table.
    """
    lines = table_text.strip().split("\n")
    headers = lines[0].strip("|").split("|")
    rows = [line.strip("|").split("|") for line in lines[1:]]

    structured_output = []
    for row in rows:
        row_data = {headers[i].strip(): row[i].strip() for i in range(len(headers))}
        structured_output.append(
            " - " + ", ".join(f"{key}: {value}" for key, value in row_data.items())
        )

    return "\n".join(structured_output)

# Example Input
page_text = """
## Project Status

This section contains the current progress.

| Phase               | Nov | Dec | Jan | Feb | Mar | Apr | May |
| Design Approval     | X   |     |     |     |     |     |     |
| Development Phase   |     | X   | X   |     |     |     |     |
| Integration Testing |     |     |     | X   |     |     |     |
| Beta Release        |     |     |     |     | X   |     |     |
| Final Release       |     |     |     |     |     |     | X   |

---

### Budget Overview

| Budget Category      | Allocated Amount (USD) | Spent Amount (USD) | % Utilized | Comments                        |
| Development          | 200,000               | 125,000             | 62.5%      | Majority spent on dev tools.   |
| Marketing            | 50,000                | 20,000              | 40%        | Initial campaign costs covered.|
| QA and Testing       | 30,000                | 5,000               | 16.7%      | Reserved for integration phase.|
| Contingency          | 20,000                | 0                   | 0%         | No emergencies to date.        |
"""

# Process and print
structured_text = process_multiple_tables_without_separator(page_text)
print(structured_text)
