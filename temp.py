import json
import re

def extract_json_from_output(llm_output):
    """
    Extract and parse the JSON content from the LLM output.
    This function can handle both raw JSON and JSON inside a code block.

    Args:
        llm_output (str): The string output from LLM, which could be raw JSON or wrapped in a code block.

    Returns:
        list: Parsed list of JSON content or empty list if parsing fails.
    """
    # First, check if the content is inside a code block (e.g., ```json)
    json_block_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(json_block_pattern, llm_output, re.DOTALL)

    if match:
        # Extract content inside the JSON block
        json_content = match.group(1).strip()
    else:
        # If no code block is found, assume the content is raw JSON
        json_content = llm_output.strip()

    # Try to parse the content as JSON
    try:
        return json.loads(json_content)
    except json.JSONDecodeError:
        print(f"Error parsing JSON content: {json_content}")
        return []
