You have the following metadata and markdown table with possible merged cells:

**Page Title**: {page_title}  
**URL**: {url}  
**Page Tree**: {page_tree}

Here is the markdown table extracted from the page:


Please:
1. Handle any merged cells (using `colspan` or `rowspan`) logically. Treat merged cells as though they are repeated for the rows/columns they span, or adjust their representation as necessary to keep the data accurate.
2. Generate a concise title for the table (only the title, no additional text).
3. Write a summary of the table (only the summary, no extra details).
4. Provide the flattened version of the data dynamically, in a list of strings, where each entry is a sentence that describes the table's rows. Each row should be formatted as: "Name: {Name}, Age: {Age}, Department: {Department}".
5. Ensure the output is structured exactly as a Python dictionary with the following format:

{
    "title": "{generated_title}",
    "summary": "{generated_summary}",
    "flattened_data": [
        "{row1_description}",
        "{row2_description}",
        "{row3_description}"
    ]
}

Please make sure that the output strictly adheres to this dictionary format and does not include any additional text or explanations.
