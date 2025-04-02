import base64
import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import ast
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_mistralai import ChatMistralAI

# Load LLM
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2
)

def load_data(file_path):
    """Loads CSV or Excel file into a DataFrame, handling errors gracefully."""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide CSV or Excel.")
        
        global df_agent
        df_agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True)
        return df
    except Exception as e:
        print(f"**ERROR:** Failed to load data - {str(e)}")
        return None

# Sample DataFrame
df = pd.DataFrame({
    'Age': [23, 45, 32, 41, 27], 
    'Salary': [50000, 80000, 60000, 75000, 65000]
})

# Initialize DataFrame agent
df_agent = create_pandas_dataframe_agent(
    llm, df, verbose=True, allow_dangerous_code=True
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
        code = code[9:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()

def check_code_safety(code):
    """Passes the generated code to the LLM for safety classification."""
    prompt = f"""
    Analyze the following Python code and determine if it contains dangerous operations.
    Dangerous operations include but are not limited to:
    - File modifications (delete, move, rename)
    - System commands execution
    - Arbitrary code execution
    - Network or subprocess operations
    - File reading/writing
    
    Code:
    ```python
    {code}
    ```
    
    Respond with only 'safe' or 'dangerous'.
    """
    response = llm.invoke(prompt)
    classification = response.content.strip().lower() if hasattr(response, "content") else str(response).strip().lower()
    
    return classification == "safe"

def generate_plot_code(query):
    """Generate valid Python plotting code using LLM."""
    prompt = f"""
    Convert the following query into a valid Python script for plotting using matplotlib and seaborn. 
    Ensure:
    - The DataFrame is named `df`
    - No explanations or markdown formatting
    - Use the correct column names from the DataFrame: {list(df.columns)}
    - Always include `plt.show()` at the end

    Query: "{query}"

    Return only the code.
    """
    response = llm.invoke(prompt)
    return clean_code(response.content if hasattr(response, "content") else str(response))

def plot_executor(query):
    """Handles plotting queries by generating and executing Python code for multiple plots."""
    try:
        plot_code = generate_plot_code(query)
        print("Generated Code:\n", plot_code)  # Debugging output
        
        if not check_code_safety(plot_code):
            return "**ERROR:** Generated code contains dangerous operations and will not be executed."

        # Ensure Matplotlib context
        exec_globals = {"df": df, "plt": plt, "sns": sns, "pd": pd}
        
        exec(plot_code, exec_globals)
        
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
    """Classifies query into 'plot', 'text', 'both', or 'invalid' using dataset context."""
    dataset_preview = df.head().to_string(index=False)
    column_stats = df.describe().to_string()
    
    classification_prompt = f"""
    Given the following dataset preview and statistics:
    
    Dataset Preview:
    {dataset_preview}
    
    Column Statistics:
    {column_stats}

    Classify the following query into 'plot', 'text', 'both', or 'invalid'.
    - If the query asks about columns that don't exist, return 'invalid'.
    - If the query is about visualization, return 'plot'.
    - If the query is about numerical/text analysis, return 'text'.
    - If the query needs both, return 'both'.

    Query: "{query}"
    
    Answer with only 'plot', 'text', 'both', or 'invalid'.
    """
    
    response = llm.invoke(classification_prompt)
    classification = response.content.strip().lower() if hasattr(response, "content") else str(response).strip().lower()
    
    return classification if classification in ["plot", "text", "both", "invalid"] else "invalid"

def route_query(query):
    """Routes query to the appropriate executor."""
    classification = classify_query(query)
    
    if classification == "invalid":
        return {"error": "Invalid query. Please check column names and try again."}
    elif classification == "both":
        return {"plot": plot_executor(query), "text": text_executor(query)}
    elif classification == "plot":
        return {"plot": plot_executor(query)}
    elif classification == "text":
        return {"text": text_executor(query)}
    
    return {"error": "Query does not match any known operations."}
