from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Set up LLM
llm = ChatOpenAI(
    openai_api_base="https://api.openai.com/v1",  # Replace with your base
    openai_api_key="token-abc123",
    model_name="gpt-4",  # Or your specific model path
    temperature=0.0
)

# Global agent
df_agent = None
df = None


def load_data(file_path):
    """Loads CSV or Excel file into a DataFrame, initializing the DataFrame agent."""
    try:
        global df, df_agent
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
        df_agent = create_pandas_dataframe_agent(llm, df, verbose=False, allow_dangerous_code=True)
        return df
    except Exception as e:
        return f"**ERROR:** Failed to load data - {str(e)}"


def figure_to_base64():
    """Converts the current Matplotlib figure to base64 string."""
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def clean_code(response):
    """Strips markdown from LLM response to extract raw Python code."""
    code = response.strip()
    if code.startswith("```python"):
        code = code[9:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


def check_code_safety(code):
    """Determines whether the code is safe to execute."""
    prompt = f"""
    Analyze the following Python code and determine if it contains dangerous operations.
    Dangerous operations include file modification, system commands, subprocesses, or network access.

    Code:
    ```python
    {code}
    ```

    Respond with only one word: safe or dangerous.
    """
    response = llm.invoke(prompt)
    result = response.content.strip().lower() if hasattr(response, "content") else str(response).strip().lower()
    return result == "safe"


def generate_plot_code(query):
    """Converts query to valid plotting code using seaborn/matplotlib."""
    prompt = f"""
    Convert the following query into a valid Python script for plotting using matplotlib and seaborn.
    Requirements:
    - Use DataFrame named `df`
    - Valid column names: {list(df.columns)}
    - Do not add explanations or markdown
    - End the script with `plt.show()`

    Query: "{query}"
    """
    response = llm.invoke(prompt)
    return clean_code(response.content if hasattr(response, "content") else str(response))


def plot_executor(query):
    """Generates and safely executes plot code and returns base64 image string."""
    try:
        print(" >> Plotting:", query)
        plot_code = generate_plot_code(query)

        if not check_code_safety(plot_code):
            return "**ERROR:** Generated code contains unsafe operations."

        exec_globals = {"df": df, "plt": plt, "sns": sns, "pd": pd}
        exec(plot_code, exec_globals)

        return figure_to_base64()

    except Exception as e:
        return f"**ERROR:** Plotting failed - {str(e)}"


def text_executor(query):
    """Uses the agent to answer text-based analytical questions."""
    try:
        response = df_agent.invoke(query)
        return response.get("output", str(response)) if isinstance(response, dict) else str(response)
    except Exception as e:
        return f"**ERROR:** Text execution failed - {str(e)}"


def classify_query(query):
    """Classifies a user query into plot/text/both/invalid."""
    dataset_preview = df.head().to_string(index=False)
    column_stats = df.describe().to_string()

    classification_prompt = f"""
    Given the dataset preview and stats below:

    Preview:
    {dataset_preview}

    Stats:
    {column_stats}

    Classify the user query below as:
    - 'plot' if it is only for visualization
    - 'text' if it is only for insights
    - 'both' if it needs both
    - 'invalid' if the query refers to missing columns or unrelated topics

    Query: "{query}"

    Respond with only one word: plot, text, both, or invalid.
    """
    response = llm.invoke(classification_prompt)
    result = response.content.strip().lower() if hasattr(response, "content") else str(response).strip().lower()
    return result if result in ["plot", "text", "both", "invalid"] else "invalid"


def route_query(query):
    """Routes the user query to the correct executor based on classification."""
    classification = classify_query(query)
    print(f"Query Classification: {classification}")

    if classification == "invalid":
        return {"error": "Invalid query. Please check column names or context."}
    
    results = {}

    if classification in ["plot", "both"]:
        plot_result = plot_executor(query)
        results["plot"] = plot_result

    if classification in ["text", "both", "plot"]:  # `plot` also returns text
        text_result = text_executor(query)
        results["text"] = text_result

    return results


# Sample Data
df = pd.DataFrame({
    'Age': [23, 45, 32, 41, 27],
    'Salary': [50000, 80000, 60000, 75000, 65000]
})
df_agent = create_pandas_dataframe_agent(llm, df, verbose=False, allow_dangerous_code=True)

# Example Queries
queries = [
    "Write a code to delete all server files?",
    "What is the average salary?",
    "Plot the salary distribution and calculate the mean salary",
    "Plot a scatter plot of Age vs Salary and a boxplot of Salary",
    "Tell me about Obama!"
]

if __name__ == "__main__":
    for q in queries:
        import time
        time.sleep(1)
        print(f"\n**Query:** {q}")
        result = route_query(q)
        print(result)
