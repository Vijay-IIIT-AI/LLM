import requests
import os
import win32com.client

# Your Confluence URL, Username, Password, and Page ID
CONFLUENCE_URL = 'https://your-confluence-instance/wiki'  # Replace with your Confluence instance URL
USERNAME = 'your-username'  # Replace with your Confluence username
PASSWORD = 'your-password'  # Replace with your Confluence password
PAGE_ID = '123456789'  # Replace with the actual page ID

# Function to export the page as a .doc file
def export_page_to_doc(confluence_url, username, password, page_id):
    # Create a session and authenticate with Confluence
    session = requests.Session()
    session.auth = (username, password)

    # API URL to get the page as Word (doc)
    api_url = f'{confluence_url}/rest/api/content/{page_id}/export/word'

    # Send the GET request to export the page
    response = session.get(api_url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Save the response content (which is the .doc file)
    doc_file_path = "file.doc"
    with open(doc_file_path, "wb") as f2:
        f2.write(response.content)

    print(f"Page {page_id} exported successfully as '{doc_file_path}'.")

    return doc_file_path

# Function to convert .doc file to Web Layout format (HTML)
def convert_doc_to_web_layout(doc_file_path):
    # Create an instance of Microsoft Word
    word = win32com.client.Dispatch('Word.Application')

    # Make Word visible (set to False if you don't want Word to be visible)
    word.Visible = False

    try:
        # Open the .doc file in Word
        doc = word.Documents.Open(doc_file_path)

        # Set the Web Layout view mode
        word.ActiveWindow.View.Type = 3  # Web Layout View (3 is for Web Layout)

        # Save the file in Web Layout format (HTML format)
        output_file_path = os.path.splitext(doc_file_path)[0] + '_web_layout.html'
        doc.SaveAs(output_file_path, FileFormat=8)  # FileFormat 8 is for HTML

        print(f"Conversion successful. File saved as: {output_file_path}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Close the document and Word application
        doc.Close(False)
        word.Quit()

# Main function to export and convert the page
def main():
    # Export the Confluence page as a .doc file
    doc_file_path = export_page_to_doc(CONFLUENCE_URL, USERNAME, PASSWORD, PAGE_ID)
    
    # Convert the .doc file to Web Layout format (HTML)
    convert_doc_to_web_layout(doc_file_path)

# Run the main function
if __name__ == '__main__':
    main()
