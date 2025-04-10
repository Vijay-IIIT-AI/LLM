from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
import pandas as pd

llm = ChatOpenAI(
    base_url="http://localhost:8000/v1",
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    api_key="fake-key"  # Just required by interface
)

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "score": [85, 92, 78]
})

agent = create_pandas_dataframe_agent(llm, df, verbose=True)
print(agent.run("Who has the highest score?"))
