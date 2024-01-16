# from langchain.llms import Ollama
from langchain_community.llms import Ollama
llm = Ollama(model="mistral")
k=llm("What is Capital of India")
print(k)