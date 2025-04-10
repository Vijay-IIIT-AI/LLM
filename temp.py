from langchain.agents import create_pandas_dataframe_agent
from langchain_community.chat_models import ChatOpenAI
import pandas as pd
import time

# Configure with proper streaming support
llm = ChatOpenAI(
    base_url="http://localhost:8000/v1",
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    api_key="no-key-required",
    temperature=0.7,
    streaming=False,  # Disable streaming for agent use
    max_retries=3,
    request_timeout=60
)

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "score": [85, 92, 78]
})

# Create agent with error handling
try:
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    response = agent.run("Who has the highest score?")
    print(response)
except Exception as e:
    print(f"Error running agent: {str(e)}")
