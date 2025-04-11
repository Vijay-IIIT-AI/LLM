docker build -t langchain-pandas-agent .


docker run --rm \
  -e OPENAI_API_BASE="http://host.docker.internal:8000/v1" \
  -e MODEL_NAME="models" \
  langchain-pandas-agent


   docker run --rm -it \
     -v /path/to/your/project:/app \
     --entrypoint bash \
     langchain-pandas-agent
