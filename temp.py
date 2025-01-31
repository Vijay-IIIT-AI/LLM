prompt = f"""
You are tasked with dividing a markdown table into smaller, manageable batches. 
Each batch should contain approximately {chunk_size} rows, ensuring that each batch includes its start and end row indices. 

Input:
A markdown table as shown below:
{input_markdown}

Output:
A JSON array where each object represents a batch with its batch number, start row index, and end row index.

Example format:
[
    {{ "batch": 1, "start": 1, "end": 5 }},
    {{ "batch": 2, "start": 6, "end": 10 }},
    ...
]

Please calculate the batch divisions and return the JSON response.
"""


system_message = "You are a data processing assistant. Your task is to divide large markdown tables into smaller, manageable batches based on a specified batch size (e.g., approximately 5 rows per batch). Each batch must include its corresponding start and end row indices.

Output the results as a JSON array, where each object contains the following fields:
- "batch": The batch number.
- "start": The starting row index of the batch.
- "end": The ending row index of the batch.

Ensure that:
1. All rows are processed, and the last batch may contain fewer rows if necessary.
2. The data is divided logically into chunks close to the specified size.

Example JSON Output:
[
    {{ "batch": 1, "start": 1, "end": 5 }},
    {{ "batch": 2, "start": 6, "end": 10 }},
    {{ "batch": 3, "start": 11, "end": 15 }}
]
"
