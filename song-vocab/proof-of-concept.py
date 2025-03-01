from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen2.5:3b",
    base_url = "http://localhost:11434"
)

messages = [
    ("system", "You are a helpful translator. Translate the user sentence to French."),
    ("human", "I love programming."),
]

print(llm.invoke(messages))
