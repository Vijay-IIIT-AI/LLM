
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



"I have scraped raw tabular data from a PDF document. Please format this data into a clean and structured markdown table, ensuring it is ready for use in a Retrieval-Augmented Generation (RAG) embedding system.

Raw Data:
Table 7. Scaled Models Used in Figure 7.
Model FLOPS Top-1 Acc.
Baseline model (EfficientNet-B0) 0.4B 77.3%
Scale model by depth (d=4) 1.8B 79.0%
Scale model by width (w=2) 1.8B 78.9%
Scale model by resolution (r=2) 1.9B 79.1%
Compound Scale (d=1.4, w=1.2, r=1.3) 1.8B 81.1%

Expected Output:
A properly formatted markdown table that organizes the scraped data into rows and columns. Ensure that the table is clean, consistent, and structured in a way that is easy to parse for RAG embedding. The output should be ready for integration into a RAG system."
