import base64
import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_mistralai import ChatMistralAI

# Load LLM
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2
)

# Sample DataFrame
df = pd.DataFrame({
    'Age': [23, 45, 32, 41, 27], 
    'Salary': [50000, 80000, 60000, 75000, 65000]
})

# Create DataFrame agent
df_agent = create_pandas_dataframe_agent(
    llm, df ,
    verbose=True,
    allow_dangerous_code=True,
)

def figure_to_base64():
    """Convert the current matplotlib figure to a base64-encoded string."""
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def clean_code(response):
    """Extracts Python code from LLM response by removing markdown and explanations."""
    code = response.strip()
    if code.startswith("```python"):
        code = code[9:]  # Remove ```python
    if code.endswith("```"):
        code = code[:-3]  # Remove ```
    return code.strip()

def generate_plot_code(query):
    """Generate valid Python plotting code using LLM."""
    prompt = f"""
    Convert the following query into a valid Python script for plotting using matplotlib and seaborn. 
    Ensure:
    - The DataFrame is named `df`
    - No explanations or markdown formatting
    - Use the correct column names from the DataFrame: {list(df.columns)}
    
    Query: "{query}"
    
    Return only the code.
    """
    response = llm.invoke(prompt)
    return clean_code(response.content if hasattr(response, "content") else str(response))

def plot_executor(query):
    """Handles plotting queries by generating and executing Python code for multiple plots."""
    try:
        plot_code = generate_plot_code(query)
        print("Generated Code:\n", plot_code)  # Debugging

        # Prepare a figure to ensure multiple plots are handled
        fig, ax = plt.subplots(figsize=(8, 6))
        exec_globals = {"df": df, "plt": plt, "sns": sns, "ax": ax}

        exec(plot_code, exec_globals)  # Execute the generated plot code
        
        return figure_to_base64()
    except Exception as e:
        return f"**ERROR:** Execution failed - {str(e)}"


def text_executor(query):
    """Handles text-based queries using the DataFrame agent."""
    try:
        response = df_agent.invoke(query)
        return response.get("output", str(response)) if isinstance(response, dict) else str(response)
    except Exception as e:
        return f"**ERROR:** Execution failed - {str(e)}"


def classify_query(query):
    """Classifies query into 'plot', 'text', or 'both'."""
    classification_prompt = f"""
    Classify the following query into 'plot', 'text', or 'both' based on its intent.
    Query: "{query}"
    Answer with only 'plot', 'text', or 'both'.
    """
    response = llm.invoke(classification_prompt)
    
    return response.content.strip().lower() if hasattr(response, "content") else str(response).strip().lower()

def route_query(query):
    """Routes query to the appropriate executor."""
    classification = classify_query(query)

    if classification == "both":
        return {"plot": plot_executor(query), "text": text_executor(query)}
    elif classification == "plot":
        return {"plot": plot_executor(query)}
    elif classification == "text":
        return {"text": text_executor(query)}
    return {"error": "Query does not match any known operations."}

# Example Usage
query1 = "Show a histogram of age distribution"
query2 = "What is the average salary?"
query3 = "Plot the salary distribution and calculate the mean salary"
query4 = "Plot a scatter plot of Age vs Salary and a boxplot of Salary"

out = route_query(query1)  # Should return base64 image
print(out)
