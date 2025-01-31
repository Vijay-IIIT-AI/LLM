def format_relevant_context(chunks, metadata_list, data_types):
    """
    Formats chunks, metadata, and data types into a "Relevant Context" structure.

    Parameters:
        chunks (list): A list of chunks (strings).
        metadata_list (list): A list of metadata dictionaries, each containing:
            - title (str): The title of the page.
            - last_updated (str): The date the page was last updated.
            - author (str): The author of the page.
            - url (str): The URL of the page.
        data_types (list): A list of data types corresponding to each chunk (e.g., 'text', 'table').

    Returns:
        str: A formatted "Relevant Context" string.
    """
    if not (len(chunks) == len(metadata_list) == len(data_types)):
        raise ValueError("All input lists must have the same length.")
    
    context = "Relevant Context:\n"
    
    for i, (chunk, metadata, data_type) in enumerate(zip(chunks, metadata_list, data_types), start=1):
        title = metadata.get("title", "No title")
        last_updated = metadata.get("last_updated", "No date")
        author = metadata.get("author", "Unknown author")
        url = metadata.get("url", "No URL")
        
        context += (
            f"{i}. Chunk (Type: {data_type}): \"{chunk}\"\n"
            f"   Title: {title}\n"
            f"   Last Updated: {last_updated}\n"
            f"   Author: {author}\n"
            f"   URL: {url}\n\n"
        )
    
    return context.strip()

# Example Usage
chunks = [
    "The onboarding process includes completing the HR forms, setting up the workstation, and attending a welcome session.",
    "New employees are assigned a buddy to help them get familiar with the company culture."
]

metadata_list = [
    {
        "title": "Onboarding Guide",
        "last_updated": "2025-01-20",
        "author": "John Doe",
        "url": "https://confluence.company.com/onboarding-guide"
    },
    {
        "title": "Buddy Program",
        "last_updated": "2025-01-15",
        "author": "Jane Smith",
        "url": "https://confluence.company.com/buddy-program"
    }
]

data_types = ["text", "text"]

# Generate and print the formatted context
relevant_context = format_relevant_context(chunks, metadata_list, data_types)
print(relevant_context)
