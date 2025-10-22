conda create -n autogen_env python=3.11 -y


# !pip install autogen-core
# !pip install autogen-agentchat
# !pip install autogen-ext
# !pip install tiktoken
# !pip install ollama
# Core AutoGen packages
!pip install autogen-core
!pip install autogen-agentchat
!pip install autogen-ext

# If you plan to use Ollama client (as in your code)
!pip install ollama
