import os
import pandas as pd
import json
import asyncio
import openpyxl  # Import openpyxl to inspect Excel files
from typing import Sequence

from autogen_core.models import ModelFamily
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.messages import TextMessage, BaseChatMessage, StopMessage

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.agents._code_executor_agent import ApprovalResponse

# =============================
# I. CONFIGURATION & SETUP
# =============================

# --- Production-Ready Configuration ---
# 1. API Key: Load from environment variables, NOT hardcoded.
#    In your terminal, run: export OPENROUTER_API_KEY='your_key_here'
#    (or set it in your system's environment variables)
api_key = "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"
if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY environment variable not set. "
        "Please set it before running the script."
    )

# 2. File Paths: Use relative paths or configurable constants, NOT absolute paths.
DATA_DIR = r"C:/Users/Vijay/Desktop/Data_Ananlysis_Agent/V2/Data"  # Store data files in a 'data' subfolder
PLOT_DIR =  r"C:/Users/Vijay/Desktop/Data_Ananlysis_Agent/V2/plots"  # Save plots to a 'plots' subfolder

# 3. Model Configuration
model_base_url = "https://openrouter.ai/api/v1"
model_name = "google/gemma-3-27b-it"

# =============================
# II. MODEL & MEMORY SETUP
# =============================
shared_memory = ListMemory()

ollama_client = OpenAIChatCompletionClient(
    model=model_name,
    base_url=model_base_url,
    api_key=api_key,
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True,
    },
)


# =============================
# III. DATASET HELPERS (UPDATED)
# =============================

def load_dataset(data_dir: str):
    """
    Loads the first valid CSV or Excel file from the specified directory.

    Performs production checks:
    - Rejects Excel files with multiple sheets.
    - Rejects Excel files containing images or graphs (drawings).
    """
    files = [f for f in os.listdir(data_dir) if f.endswith((".csv", ".xlsx"))]
    if not files:
        raise FileNotFoundError(f"No CSV or Excel files found in the '{data_dir}' folder")

    dataset_file = os.path.join(data_dir, files[0])
    print(f"Loading dataset: {dataset_file}")

    if dataset_file.endswith(".csv"):
        df = pd.read_csv(dataset_file, header=0)
    else:
        # --- Handle Negative Cases for Excel ---
        try:
            # 1. Check for multiple sheets
            xls = pd.ExcelFile(dataset_file)
            if len(xls.sheet_names) > 1:
                raise ValueError(
                    f"Excel file '{files[0]}' contains multiple sheets. "
                    "Only single-sheet Excel files are allowed."
                )

            # 2. Check for images/graphs using openpyxl
            workbook = openpyxl.load_workbook(dataset_file)
            sheet = workbook.active
            if sheet._images or sheet._charts:
                raise ValueError(
                    f"Excel file '{files[0]}' contains images or charts. "
                    "Complex Excel files are not allowed."
                )

            # If checks pass, load the first sheet
            df = pd.read_excel(dataset_file, header=0, sheet_name=0)

        except Exception as e:
            print(f"Error loading Excel file: {e}")
            raise

    return dataset_file, df


def verify_dataset(df: pd.DataFrame):
    """Generates a verification report for the DataFrame."""
    return {
        "shape": df.shape,
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "head": df.head(3).to_dict(orient="records"),
    }


# =============================
# IV. AGENT DEFINITIONS (UPDATED)
# =============================
manager_agent = AssistantAgent(
    "manager", ollama_client, memory=[shared_memory],
    system_message=(
        "You are the manager. Take the user question, decide the flow, "
        "coordinate other agents, and finally return the raw answer.\n"
        "- IMPORTANT: When you are confident the final answer is ready, "
        "explicitly forward it to the 'returner' agent for beautification.\n"
        "- Do not beautify yourself, just pass the plain result."
    ),
)

data_analysis_agent = AssistantAgent(
    "analysis", ollama_client, memory=[shared_memory],
    system_message="Interpret the user’s question and decide the required analysis."
)

# --- Updated Coding Agent Prompt ---
coding_agent = AssistantAgent(
    "coder", ollama_client, memory=[shared_memory],
    system_message=(
        f"You are the coding agent.\n"
        f"- If the user asks for a plot, use matplotlib (not seaborn).\n"
        f"- Always save the plot as a PNG file under the '{PLOT_DIR}/' directory "
        f"with a descriptive filename based on the question.\n"
        f"- Example: '{PLOT_DIR}/age_distribution.png'.\n"
        f"- After saving, print exactly: 'Plot saved at: <filepath>'.\n"
        f"- Always close the figure after saving with plt.close().\n"
        f"- If it's a stats question, compute and print the result clearly.\n"
    ),
)

executor = LocalCommandLineCodeExecutor(work_dir="workspace", timeout=600)

# --- WARNING: Auto-approval is NOT production-safe ---
# For real production, use a human-in-the-loop approval function.
# approval_func=lambda code: ApprovalResponse(approved=input("Approve code? (y/n)") == 'y')
executor_agent = CodeExecutorAgent(
    "executor",
    code_executor=executor,
    approval_func=lambda code: ApprovalResponse(
        approved=True,  # DANGEROUS for production
        reason="Auto-approved for execution (DEV ONLY)"
    )
)

qc_agent = AssistantAgent(
    "qc", ollama_client, memory=[shared_memory],
    system_message=(
        "You are the QC agent.\n"
        "- If the executor printed 'Plot saved at: ...', confirm that the file exists.\n"
        "- Then report: '✅ Plot generated successfully at <filepath>'.\n"
        "- If it’s numeric output, verify correctness and summarize clearly.\n"
        "- Always forward the validated result to the 'manager'."
    ),
)

return_agent = AssistantAgent(
    "returner", ollama_client, memory=[shared_memory],
    system_message=(
        "You are the return agent.\n"
        "- Take the final validated answer from Manager.\n"
        "- Beautify it in **Markdown format**.\n"
        "- Use bullet points, bold text, and tables if helpful.\n"
        "- Keep the response clear and structured.\n"
        "- This is the final answer shown to the user."
    ),
)

terminator_agent = AssistantAgent(
    "terminator", ollama_client, memory=[shared_memory],
    system_message="You are the termination agent. Stop the workflow after the 'returner' agent provides the final beautified Markdown answer."
)

human_agent = UserProxyAgent(name="human", input_func=lambda prompt=None: "")


# =============================
# V. TERMINATION CONDITION
# =============================
class StopWhenAnswered:
    """Terminates the chat when the 'returner' agent provides a response."""
    def __init__(self):
        self._terminated = False

    @property
    def terminated(self):
        return self._terminated

    async def __call__(self, messages: Sequence[BaseChatMessage]):
        for msg in messages:
            if isinstance(msg, TextMessage):
                # Terminate if the 'returner' has spoken and its content is not empty
                if msg.source == "returner" and len((msg.content or "").strip()) > 10:
                    self._terminated = True
                    return StopMessage(
                        source="terminator",
                        content="Workflow stopped: Final beautified Markdown answer delivered."
                    )
        return None

    async def reset(self):
        self._terminated = False


# =============================
# VI. TEAM SETUP
# =============================
team = SelectorGroupChat(
    participants=[
        manager_agent, data_analysis_agent, coding_agent,
        executor_agent, qc_agent, return_agent, human_agent
    ],
    model_client=ollama_client,
    termination_condition=StopWhenAnswered(),
    max_turns=40,
)


# =============================
# VII. MAIN EXECUTION (UPDATED)
# =============================
async def main():
    # --- Create directories if they don't exist ---
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR, exist_ok=True)
    os.makedirs("workspace", exist_ok=True)  # For the code executor

    try:
        dataset_file, df = load_dataset(DATA_DIR)
        verify_report = verify_dataset(df)
        sample_info = json.dumps(verify_report, indent=2)

        await shared_memory.add(
            MemoryContent(
                content=f"Dataset file: {dataset_file}\nVerification summary:\n{sample_info}",
                mime_type=MemoryMimeType.TEXT,
            )
        )

        user_question = "For passengers who paid more than £50 fare (wealthy group), compare survival of males vs females. Was being male still a strong negative factor even when wealthy, or did money overcome gender disadvantage?"

        task_prompt = f"""
        Dataset file: {dataset_file}

        Verification summary:
        {sample_info}

        User Question: {user_question}

        Instructions:
        - Manager coordinates and forwards final raw answer to Returner.
        - Analysis interprets.
        - Coder writes code (saving plots to '{PLOT_DIR}').
        - Executor runs code.
        - QC validates and passes to Manager.
        - Manager forwards to Returner.
        - Returner beautifies in Markdown.
        - Terminator stops workflow when Returner is done.
        - No JSON, only plain human-readable answer.

          Important Instructions (Handling User Questions):
        - ** First row may not be always header - so handle it accoridly in all codes - think in all direction user may have merged cells or normal data etc..,(eg. create a correct mapping of coloumn names after handling the rows** 
        - **Analyze user intent first.** Your primary goal is to answer questions *about the provided dataset*.
        - **Plots:** Only generate a plot if the user *explicitly* asks for a "plot," "chart," "graph," or "visualization." Do not generate plots for simple statistical questions.
        - **Relevance:** If the user's question is irrelevant to the dataset (e.g., "What is the capital of France?", "Who are you?"), you MUST reject it. State that you can only answer questions about the loaded data.
        - **Complexity:** This is a data analysis agent, not a machine learning platform. You MUST reject complex, out-of-scope requests like:
            - "Train a machine learning model."
            - "Build a predictive model."
            - "Perform deep learning."
            - Any other complex AI or model training tasks.
        - **If a question is rejected:** The 'manager' or 'analysis' agent should state *why* it is being rejected (e.g., "This question is out of scope. I can only analyze the provided dataset.") and then forward this rejection message to the 'returner' to be delivered to the user.
        """
       

        print("\n=== STARTING DATA ANALYSIS WORKFLOW ===\n")
        print(f"Data Dir: {os.path.abspath(DATA_DIR)}")
        print(f"Plot Dir: {os.path.abspath(PLOT_DIR)}")
        print(f"User Question: {user_question}\n")
        print("--- Agent Conversation ---")

        async for msg in team.run_stream(task=task_prompt):
            if hasattr(msg, "content") and hasattr(msg, "source"):
                print(f"[{msg.source.upper()}]: {msg.content}\n")

    except (FileNotFoundError, ValueError) as e:
        print(f"\n=== WORKFLOW PREPARATION FAILED ===\nError: {e}")
    except Exception as e:
        print(f"\n=== WORKFLOW ERROR ===\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user (CTRL+C). Exiting gracefully...")
