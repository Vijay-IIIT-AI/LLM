import html2text

# Initialize html2text converter
converter = html2text.HTML2Text()
converter.ignore_links = True  # Optionally ignore hyperlinks
converter.ignore_images = True  # Optionally ignore images

# Read the HTML file
with open("example.html", "r", encoding="utf-8") as html_file:
    html_content = html_file.read()

# Convert HTML to plain text
plain_text = converter.handle(html_content)

# Print or save the plain text
print(plain_text)
