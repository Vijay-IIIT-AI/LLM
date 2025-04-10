from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
import pandas as pd

# Connect to your local FastAPI server
llm = ChatOpenAI(
    base_url="http://localhost:8000/v1",  # Your FastAPI endpoint
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    api_key="no-key-required",  # Not used but required by interface
    temperature=0.7  # You can adjust generation parameters here
)

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "score": [85, 92, 78]
})

agent = create_pandas_dataframe_agent(llm, df, verbose=True)
print(agent.run("Who has the highest score?"))
