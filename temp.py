from io import BytesIO
excel_buffer = BytesIO()
wb.save(excel_buffer)
excel_buffer.seek(0)  # Move the pointer back to the beginning

# Read the workbook into pandas
df = pd.read_excel(excel_buffer, engine='openpyxl')
print(df)
