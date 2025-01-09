import re

def detect_complex_markdown(content):
    # Detect tables
    table_pattern = r"^\|.*\|$"
    tables = [line for line in content.splitlines() if re.match(table_pattern, line)]

    # Detect unordered lists
    list_pattern = r"^\s*[*+-]\s+.*"
    unordered_lists = [line for line in content.splitlines() if re.match(list_pattern, line)]

    # Detect mixed structures (e.g., list items near tables)
    mixed_structures = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if re.match(list_pattern, line) or re.match(table_pattern, line):
            context = "\n".join(lines[max(0, i - 1):min(len(lines), i + 2)])
            mixed_structures.append(context)

    return {
        "tables": tables,
        "unordered_lists": unordered_lists,
        "mixed_structures": mixed_structures,
    }

# Sample complex markdown
markdown_text = """
---|---|---
* some content  
| | some | some
* some content
| | some | some
"""

# Detect markdown elements
detected_elements = detect_complex_markdown(markdown_text)

# Display results

print("\nMixed Structures Found:")
print("\n".join(detected_elements["mixed_structures"]))

