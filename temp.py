
### Prompt:

**Context:**  
I have a table written in markdown format. I need help extracting two pieces of information:  
1. A meaningful title for the table based on its content.  
2. A concise summary that explains what the table represents.

**Instructions for the LLM:**  
1. Analyze the table to infer an appropriate title that reflects its content and purpose.  
2. Provide a brief summary (1-3 sentences) describing the table, focusing on the type of data, its context, and any key observations.

**Example Input:**  
```markdown
| Date       | Product Name | Sales ($) | Region       |  
|------------|--------------|-----------|--------------|  
| 2025-01-01 | Product A    | 1500      | North America|  
| 2025-01-02 | Product B    | 2000      | Europe       |
```

**Desired Output:**  
**Title:** "Sales Performance by Product and Region"  
**Summary:** This table presents sales data for various products across different regions. It includes information about sales amounts (in dollars) and corresponding dates, offering insight into performance trends over time.

**Input Template:**  
"Here is a markdown table:  
```markdown  
[Insert your markdown table here]  
```  
Based on this table, please provide:  
1. A meaningful title for the table.  
2. A concise summary describing the table's purpose and content."

---
