def clean_code(response_text):
    """Extracts and cleans raw Python code from LLM output."""
    code = response_text.strip()

    # Remove Markdown code block if present
    if "```" in code:
        code = code.split("```")
        code = [c for c in code if not c.strip().lower().startswith("python")]
        code = "".join(code)

    return code.strip()

def plot_executor(query):
    """Generates and safely executes plotting code from a query."""
    try:
        print(" >> Plotting:", query)

        plot_code = generate_plot_code(query)
        plot_code = clean_code(plot_code)
        print("Generated Plot Code:\n", plot_code)

        # Safety check
        if not check_code_safety(plot_code):
            return "**ERROR:** Generated code contains unsafe operations."

        # Syntax check before execution
        try:
            compile(plot_code, "<string>", "exec")
        except SyntaxError as se:
            return f"**ERROR:** Syntax error in generated code - {str(se)}"

        # Execution
        exec_globals = {"df": df, "plt": plt, "sns": sns, "pd": pd}
        exec(plot_code, exec_globals)

        return figure_to_base64()

    except Exception as e:
        return f"**ERROR:** Plotting failed - {str(e)}"
