import requests
from docx import Document

# Confluence credentials and URL
CONFLUENCE_URL = 'https://your-confluence-instance/wiki'
API_URL = f'{CONFLUENCE_URL}/rest/api/content'
PAGE_ID = '123456789'  # Replace with the actual page ID
USERNAME = 'your-username'
PASSWORD = 'your-password'

# Create a session and authenticate with Confluence
session = requests.Session()
session.auth = (USERNAME, PASSWORD)

# Fetch page content from Confluence
response = session.get(f'{API_URL}/{PAGE_ID}?expand=body.storage')
response.raise_for_status()  # Ensure we got a successful response

# Extract page title and content
page_data = response.json()
page_title = page_data['title']
page_content = page_data['body']['storage']['value']

# Create a new Word document
doc = Document()
doc.add_heading(page_title, 0)

# Add page content to the Word document
doc.add_paragraph(page_content)

# Add the page ID to the footer
footer = doc.sections[0].footer
footer.paragraphs[0].text = f"Page ID: {PAGE_ID}"

# Save the document as a .docx file
doc.save(f'{page_title}.docx')

print(f"Page '{page_title}' downloaded as Word document.")
