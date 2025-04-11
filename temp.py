import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# Set environment variables or use defaults
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:8000/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy")  # vLLM doesn't require this, but LangChain expects it
MODEL_NAME = os.getenv("MODEL_NAME", "models")  # Replace with your actual model name if different

# Create a sample DataFrame
data = {
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Ethan"],
    "Age": [25, 30, 35, 40, 45],
    "Department": ["HR", "Engineering", "Marketing", "Finance", "IT"]
}
df = pd.DataFrame(data)

# Initialize the language model
llm = ChatOpenAI(
    model=MODEL_NAME,
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_API_BASE,
    temperature=0,
)

# Create the pandas dataframe agent
agent = create_pandas_dataframe_agent(
    llm=llm,
    df=df,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Query the agent
response = agent.invoke("What is the average age of employees?")
print(response)
