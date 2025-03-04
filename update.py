prompt = (
    "Extract all texts from this presentation slide (literal extraction, do not summarize!) and tabular data. "
    "When an image or diagram is present, describe it, and extract any visible text. "
    "When a graph with data is present: "
    "- Identify the type of graph (bar chart, line chart, pie chart, etc.). "
    "- Extract axis labels, key numerical values, and trends. "
    "- Provide key insights or messages from the graph. "
    "Text inside a diagram or graph should only be extracted within its specific context (not as regular slide text). "
    " "
    "### JSON Output Format: "
    "Ensure your response follows this structure exactly, and output valid JSON only (no backticks). "
    "[ "
    "    { "
    '        "slide_title": "Example Slide Title", '
    '        "subheading": "Example Slide Subheading", '
    '        "text": "Example text content extracted from slide.", '
    '        "images": [ '
    '            "Description of the first image or diagram.", '
    '            "Description of the second image or diagram." '
    "        ], "
    '        "graphs": [ '
    "            { "
    '                "type": "line_chart", '
    '                "title": "Example Graph Title", '
    '                "x_axis": "Time (Years)", '
    '                "y_axis": "Revenue ($M)", '
    '                "key_values": { '
    '                    "2020": "5M", '
    '                    "2021": "7M", '
    '                    "2022": "10M" '
    "                }, "
    '                "trend": "Steady revenue increase over three years." '
    "            } "
    "        ], "
    '        "tables": [ '
    "            { "
    '                "columns": ["Category", "Value"], '
    '                "rows": [ '
    '                    ["Revenue", "$10M"], '
    '                    ["Growth Rate", "15%"] '
    "                ] "
    "            } "
    "        ] "
    "    } "
    "] "
    " "
    "### Rules for Extraction: "
    "1. Do NOT summarize any extracted text. "
    '2. Do NOT include "tables", "graphs", or "images" if they are not present in the slide. '
    "3. Ensure all extracted data is structured properly for later retrieval."
)
