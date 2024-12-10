from openpyxl import Workbook

def create_excel(space, pages):
    page_levels = max(page.level for page in pages)
    
    # Create a new workbook and select the active worksheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"{space}_Hierarchy"
    
    # Define field names for the header row
    fieldnames = [f'Tree depth {level}' for level in range(page_levels+1)]
    fieldnames.append('URL')
    
    # Write the header row
    sheet.append(fieldnames)
    
    # Write each page's data into the worksheet
    for page in pages:
        link = site + page.url
        row_data = ["" for _ in range(page_levels + 1)]
        row_data[page.level] = page.title  # Insert the title at the correct level
        row_data.append(link)  # Append the URL
        sheet.append(row_data)
    
    # Save the workbook to a file
    workbook.save(f'./{space}_hierarchy.xlsx')
