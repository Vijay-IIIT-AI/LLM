def generate_plot_code(query):
    """Convert a query into valid Python plotting code using matplotlib and seaborn."""
    prompt = f"""
    You are a Python plotting assistant. Convert the user query into pure, valid Python code using matplotlib and seaborn.

    - Use the DataFrame named `df`
    - Valid columns: {list(df.columns)}
    - No markdown or explanation—return only executable Python code
    - End with `plt.show()`
    - Do NOT return multiple code snippets. Only a single complete script.

    Query: "{query}"

    Output:
    """
    response = llm.invoke(prompt)
    raw_code = response.content if hasattr(response, "content") else str(response)
    return clean_code(raw_code)
