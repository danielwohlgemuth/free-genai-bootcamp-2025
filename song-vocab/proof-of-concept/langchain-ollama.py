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
# Output: content="J'aime programmer." additional_kwargs={} response_metadata={'model': 'qwen2.5:3b', 'created_at': '2025-03-01T01:31:55.314646347Z', 'done': True, 'done_reason': 'stop', 'total_duration': 2352203001, 'load_duration': 29523792, 'prompt_eval_count': 30, 'prompt_eval_duration': 2042000000, 'eval_count': 6, 'eval_duration': 275000000, 'message': Message(role='assistant', content='', images=None, tool_calls=None)} id='run-306e9336-bea0-4824-b4d2-5a00d199db93-0' usage_metadata={'input_tokens': 30, 'output_tokens': 6, 'total_tokens': 36}
