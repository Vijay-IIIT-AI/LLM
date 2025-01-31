import openai
import json

# Function to flatten a specific batch and return the flattened data
def flatten_batch_with_llm(batch, markdown_table, last_batch=None):
    # Construct the prompt to pass to the LLM, including the last batch for continuity
    prompt = f"""
    Given the following markdown table, flatten the data into a structured JSON format for the specified batch.

    Batch details: {batch}
    
    Last processed batch (optional): {last_batch if last_batch else "None"}
    
    Here is the full table:

    ```
    {markdown_table}
    ```

    Your task is to:
    1. Extract rows from the table based on the 'start' and 'end' values in the batch.
    2. Flatten the extracted rows into a structured JSON format.
    3. Ensure consistency by referencing the last processed batch if necessary.
    
    Return a JSON array of objects representing each row in the table.
    """

    try:
        # Send the prompt to the LLM (you can replace with your API call)
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Choose your desired model
            messages=[
                {"role": "system", "content": "You are an assistant that flattens markdown tables into structured JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        # Extract and return the flattened JSON data
        flattened_data = json.loads(response["choices"][0]["message"]["content"])
        return flattened_data

    except Exception as e:
        print(f"Error processing batch {batch['batch']}: {e}")
        return []

# Example markdown table (replace with your actual markdown string)
markdown_table = """
Column1 | Column2 | Column3
--------|---------|--------
Value1  | Value2  | Value3
Value4  | Value5  | Value6
Value7  | Value8  | Value9
Value10 | Value11 | Value12
Value13 | Value14 | Value15
Value16 | Value17 | Value18
"""

# Example batch information
batch_iterations = [
    {'batch': 1, 'start': 1, 'end': 5},
    {'batch': 2, 'start': 6, 'end': 10},
    # Add more batches as needed
]

# Store the final output after flattening all batches
final_flattened_output = []

# Variable to keep track of the last batch processed
last_batch = None

# Process each batch and flatten the corresponding rows
for batch in batch_iterations:
    print(f"Processing Batch {batch['batch']}...")
    
    # Flatten the data for this batch
    flattened_batch = flatten_batch_with_llm(batch, markdown_table, last_batch)
    
    # Append the flattened data to the final output
    if flattened_batch:
        final_flattened_output.extend(flattened_batch)

    # Update the last processed batch
    last_batch = batch

# Save the flattened data to a JSON file (optional)
with open("flattened_data.json", "w") as f:
    json.dump(final_flattened_output, f, indent=4)

print("All batches processed and flattened successfully!")
