#%% Data Analysis Agent Workflow (with Auto-Termination + Planner + QC Repair)
import os
import pandas as pd
import json
import asyncio
from typing import Sequence, Optional

from autogen_core.models import ChatCompletionClient, ModelFamily
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.messages import TextMessage, BaseChatMessage, StopMessage

# --- NEW: environment-based configuration (production-friendly) ---
OUTPUT_DIR = os.getenv("PLOTS_DIR", r"C:\Users\Vijay\Desktop\Plots")
INTERACTIVE = os.getenv("INTERACTIVE", "false").lower() == "true"
DATA_DIR = os.getenv("DATA_DIR", r"C:\Users\Vijay\Desktop\Data")

# === MODEL CLIENT (unchanged except small safety notes) ===
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

shared_memory = ListMemory()

# If you switch providers, prefer ENV vars and avoid hard-coded secrets in production.
# Example:
#   model_base_url = os.getenv("MODEL_BASE_URL", "https://openrouter.ai/api/v1")
#   api_key = os.getenv("OPENROUTER_API_KEY")
#   model_name = os.getenv("MODEL_NAME", "google/gemma-3-27b-it")

model_base_url = "https://openrouter.ai/api/v1"
api_key = "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"
model_name = "google/gemma-3-27b-it"

# NOTE: Some versions of autogen_ext are strict about ModelFamily matching.
# If you see a "model family" error, remove the 'family' field below or set
# it to a generic/compatible value for your installed version.
ollama_client = OpenAIChatCompletionClient(
    model=model_name,
    base_url=model_base_url,
    api_key=api_key,
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.LLAMA_3_3_70B,  # <- Mismatch with Gemma in some versions.
        "structured_output": True,
        "multiple_system_messages": True,
    },
)

# =============================
# II. DATASET HELPERS
# =============================
def load_dataset(data_dir=DATA_DIR):
    files = [f for f in os.listdir(data_dir) if f.endswith((".csv", ".xlsx"))]
    if not files:
        raise FileNotFoundError(f"No CSV/Excel files found in {data_dir}")

    dataset_file = os.path.join(data_dir, files[0])
    if dataset_file.endswith(".csv"):
        df = pd.read_csv(dataset_file, header=0)
    else:
        df = pd.read_excel(dataset_file, header=0)

    return dataset_file, df


def verify_dataset(df: pd.DataFrame):
    return {
        "shape": df.shape,
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "head": df.head(3).to_dict(orient="records"),
    }


# =============================
# III. AGENT DEFINITIONS
# =============================

# --- NEW: Planner agent (decomposes problem into explicit, ordered steps) ---
planner_agent = AssistantAgent(
    "planner",
    ollama_client,
    memory=[shared_memory],
    system_message=(
        "You are the Planner. Decompose the user's question into a concise, "
        "ordered, actionable plan of steps the team should follow. "
        "Be explicit about: data preparation, validation, analysis, and outputs. "
        "Do not write code. Do not execute. Keep it short and numbered."
    ),
)

manager_agent = AssistantAgent(
    "manager", ollama_client, memory=[shared_memory],
    system_message=(
        "You are the Manager. Use the Planner's steps to coordinate other agents "
        "and deliver a final human-readable answer. Ask the Coder to implement, "
        "Executor to run, and QC to verify. Summarize results clearly at the end."
    ),
)

data_analysis_agent = AssistantAgent(
    "analysis", ollama_client, memory=[shared_memory],
    system_message="Interpret the user’s question, validate columns/assumptions, and propose the exact computations."
)

# --- UPDATED: Coder reads OUTPUT_DIR from memory and saves plots there ---
coding_agent = AssistantAgent(
    "coder", ollama_client, memory=[shared_memory],
    system_message=(
        "You are the Coding agent.\n"
        "- Use pandas/matplotlib only. (Do NOT use seaborn.)\n"
        "- All plots must be saved under the OUTPUT_DIR provided in shared memory.\n"
        "- Build descriptive filenames based on the user question; slugify safely.\n"
        "- After saving, print exactly: 'Plot saved at: <filepath>'.\n"
        "- Always call plt.close() after saving.\n"
        "- For numeric/statistical answers, print the result clearly to stdout.\n"
        "- If a column is missing, gracefully handle KeyError and print a helpful message."
    ),
)

# --- EXECUTOR: Prefer DockerCommandLineCodeExecutor in production for isolation ---
executor = LocalCommandLineCodeExecutor(work_dir="workspace", timeout=600)
executor_agent = CodeExecutorAgent("executor", code_executor=executor)

# --- UPDATED: QC with repair loop logic ---
qc_agent = AssistantAgent(
    "qc", ollama_client, memory=[shared_memory],
    system_message=(
        "You are the QC agent.\n"
        "- Inspect the latest executor output and any files reported.\n"
        "- If output contains 'Traceback' or 'Error' or indicates missing columns, "
        "summarize the issue and instruct the Coder exactly how to fix it (edit code).\n"
        "- If a 'Plot saved at: <filepath>' line appears, ask the Manager to announce success.\n"
        "- For numeric outputs, verify they make sense given dataset verification summary and restate the result.\n"
        "- Be concise and decisive."
    ),
)

# Termination agent (kept for completeness; actual stopping is in StopWhenAnswered)
terminator_agent = AssistantAgent(
    "terminator", ollama_client, memory=[shared_memory],
    system_message=(
        "You are the termination agent. Monitor the conversation. "
        "If the user question has been answered clearly (e.g., confirmed plot path or final numeric answer), "
        "the workflow should stop."
    ),
)

# --- UPDATED: Human-in-the-loop toggle (interactive vs batch) ---
human_agent = UserProxyAgent(
    name="human",
    input_func=(lambda prompt=None: input(prompt)) if INTERACTIVE else (lambda prompt=None: "")
)


# =============================
# IV. TERMINATION CONDITION
# =============================
class StopWhenAnswered:
    """
    Stop when Manager or QC delivers a substantial final answer OR when a plot path is confirmed.
    """
    def __init__(self):
        self._terminated = False

    @property
    def terminated(self):
        return self._terminated

    async def __call__(self, messages: Sequence[BaseChatMessage]):
        for msg in messages:
            if isinstance(msg, TextMessage):
                content = (msg.content or "").strip()
                if not content:
                    continue
                # Clear stop signals:
                if "✅ Plot generated successfully at" in content:
                    self._terminated = True
                    return StopMessage(source="terminator", content="Workflow stopped: plot generated and confirmed.")
                if msg.source in {"manager", "qc"} and len(content) > 20:
                    # Heuristic: final-looking message
                    if any(kw in content.lower() for kw in ["final answer", "result:", "answer:", "summary:"]):
                        self._terminated = True
                        return StopMessage(source="terminator", content="Workflow stopped: final answer delivered.")
        return None

    async def reset(self):
        self._terminated = False


# =============================
# V. TEAM SETUP (added planner)
# =============================
team = SelectorGroupChat(
    [planner_agent, manager_agent, data_analysis_agent, coding_agent, executor_agent, qc_agent, human_agent],
    model_client=ollama_client,
    termination_condition=StopWhenAnswered(),
    max_turns=40,
)


# =============================
# VI. MAIN EXECUTION
# =============================
async def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dataset_file, df = load_dataset(DATA_DIR)
    verify_report = verify_dataset(df)
    sample_info = json.dumps(verify_report, indent=2)

    # --- Share grounding info + OUTPUT_DIR to all agents via memory ---
    await shared_memory.add(
        MemoryContent(
            content=(
                f"Dataset file: {dataset_file}\n"
                f"Verification summary:\n{sample_info}\n"
                f"OUTPUT_DIR for plots: {OUTPUT_DIR}\n"
            ),
            mime_type=MemoryMimeType.TEXT,
        )
    )

    # Example user question (kept from your original)
    user_question = "What is the age of my firend Nysten ?"

    # --- Task prompt now nudges Planner first, then the rest of the team ---
    task_prompt = f"""
        You are a team. Follow this order: Planner -> Manager -> Analysis -> Coder -> Executor -> QC -> Manager.
        Dataset file: {dataset_file}

        Verification summary:
        {sample_info}

        User Question: {user_question}

        Instructions:
        - Planner: produce a short numbered plan that the team should follow.
        - Manager: coordinate according to the plan; call on Analysis/Coder/Executor/QC as needed.
        - Analysis: interpret the question precisely; clarify columns needed and computations.
        - Coder: write Python using pandas/matplotlib only. Save plots to OUTPUT_DIR and print 'Plot saved at: <filepath>'.
        - Executor: run the code and print stdout/stderr.
        - QC: validate outputs. If errors (Traceback/Error/missing columns), instruct Coder how to fix and retry.
        - Manager: deliver a concise final answer ('Final answer: ...').
        - Terminator/StopWhenAnswered will stop once final answer/plot success is reported.

        Notes:
        - OUTPUT_DIR (for all plots): {OUTPUT_DIR}
        - Do NOT output JSON; use clear human-readable text only.
        """

    print("\n=== STARTING DATA ANALYSIS WORKFLOW ===\n")
    async for msg in team.run_stream(task=task_prompt):
        if hasattr(msg, "content") and hasattr(msg, "source"):
            print(f"[{msg.source.upper()}]: {msg.content}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user (CTRL+C). Exiting gracefully...")
