import re

def convert_table_to_structured_text(table_text):
    """
    Convert a Markdown table to structured text.

    Args:
        table_text (str): The Markdown table as a string.

    Returns:
        str: Structured text representing the table's content.
    """
    # Split the table into lines and process
    lines = table_text.strip().split('\n')
    headers = lines[0].strip('|').split('|')  # Extract headers
    rows = [line.strip('|').split('|') for line in lines[2:]]  # Skip separator line

    # Clean whitespace and convert each row
    structured_rows = []
    for row in rows:
        row_text = ', '.join([f"{headers[i].strip()}: {cell.strip()}" for i, cell in enumerate(row)])
        structured_rows.append(f"- {row_text}")

    return '\n'.join(structured_rows)

def enrich_markdown_table_with_structured_text(markdown_text):
    """
    Replace Markdown tables in a document with their structured text equivalent.

    Args:
        markdown_text (str): The Markdown document containing tables.

    Returns:
        str: The Markdown document with tables converted to structured text.
    """
    enriched_markdowns = []
    table_regex = r"(.*?)(\|[^\n]+\|(?:\n\|[^\n]+\|)+)"
    matches = re.findall(table_regex, markdown_text, flags=re.DOTALL)

    for match in matches:
        surrounding_text = match[0].strip()
        table_text = match[1].strip()

        # Convert the table to structured text
        structured_text = convert_table_to_structured_text(table_text)

        # Reformat enriched table with structured text
        enriched_table = f"{surrounding_text}\n\n{structured_text}\n"
        enriched_markdowns.append(enriched_table)

    return "\n".join(enriched_markdowns)

# Example Markdown with tables
markdown_text = """
"""
# """

# Process the Markdown
enriched_markdown = enrich_markdown_table_with_structured_text(markdown_text)
print(enriched_markdown)
