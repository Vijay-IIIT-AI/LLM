import re

# Sample input with multiple tables
text = """
# Product Inventory Report

## Introduction
This report provides a detailed view of our product inventory and pricing across various categories. Below, you'll find tables showcasing different formats of product data.

---

## Case 1: Missing Header (C1 is empty)
This section showcases a table where the first column (C1) is missing. Here, the table represents products with their price and quantity.

| Product  | Price | Quantity |
| ---      | ---   | ---     |
| Apple    | $2    | 50      |
| Banana   | $1    | 100     |
| Orange   | $3    | 30      |

If `C1` is provided, the following format is used:

|  | Product  | Price | Quantity |
| --- | ---      | ---   | ---     |
| 001 | Apple    | $2    | 50      |
| 002 | Banana   | $1    | 100     |
| 003 | Orange   | $3    | 30      |

---

## Case 2: Starting and Ending No Pipe
Here, the table does not have starting and ending pipes. However, the data remains readable.

ID    | Product  | Price | Quantity  
---   | ---      | ---   | ---   
001   | Apple    | $2    | 50  
002   | Banana   | $1    | 100  
003   | Orange   | $3    | 30  

---

## Case 3: No Header Splitter and No Starting/Ending Pipe
In this case, we omit the header splitter, and the table format is simplified without the starting and ending pipes.

ID    | Product  | Price | Quantity  
001   | Apple    | $2    | 50  
002   | Banana   | $1    | 100  
003   | Orange   | $3    | 30  
004   | Mango    | $4    | 20  

---

## Case 4: Proper Markdown Format
This is the standard format for markdown tables, where headers and splitters are used, providing a clean layout for data.

| ID  | Product  | Price | Quantity |
| --- | ---      | ---   | ---     |
| 001 | Apple    | $2    | 50      |
| 002 | Banana   | $1    | 100     |
| 003 | Orange   | $3    | 30      |

---

## Case 5: Header Added Below
In this case, the headers are placed below the table. This is still a valid markdown format but doesn't follow the usual convention.

|   |   |   |
|---|---|---|
| ID | Product | Price |
| 001 | Apple   | $2    |
| 002 | Banana  | $1    |

---
"""

# Regular expression to match tables separated by empty lines
regex = r'((?:[^\n]*\|[^\n]*\|[^\n]*\n?)+)'

# Find all tables
tables = re.findall(regex, text.strip())

pure_text = re.sub(regex, '', text)
print(pure_text)

# Print the matched tables
for table in tables:
    print(table.strip())
    print("-my--")
