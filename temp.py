def plot_executor(query):
    """Generates and safely executes plotting code from a query."""
    try:
        print(" >> Plotting:", query)
        plot_code = generate_plot_code(query)
        print("Generated Plot Code:\n", plot_code)  # helpful for debugging

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
