import langchain
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.tools import tool, StructuredTool
from typing import Annotated, Optional

# langchain.debug = True

system_template = """
You are an assistant that only calls the tool `the_tool` on each interaction and nothing else.
Return the result of the tool call.
"""

model = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen2.5:7b"
)

def tool(user_id: Optional[str] = None, haiku_id: Optional[str] = None) -> str:
    return f"user_id: {user_id}, haiku_id: {haiku_id}"

def create_configured_tool(user_id, haiku_id):
    def configured_tool():
        return tool(user_id, haiku_id)
    
    return StructuredTool.from_function(
        func=configured_tool,
        name="the_tool",
        description="A tool that responds with a user ID and haiku ID.",
        args_schema=None
    )

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("placeholder", "{messages}"),
    ("placeholder", "{agent_scratchpad}"),
])

def create_agent_with_params(user_id, haiku_id):
    configurable_tool = create_configured_tool(user_id, haiku_id)
    
    agent_model = create_tool_calling_agent(model, tools=[configurable_tool], prompt=prompt)
    agent_executor = AgentExecutor(agent=agent_model, tools=[configurable_tool], verbose=False, max_iterations=5)
    
    return agent_executor

input = {"messages": [("human", "Hi. What does the tool say?")]}

# First invocation with specific IDs
agent_executor_1 = create_agent_with_params("user123", "haiku456")
result_1 = agent_executor_1.invoke(input)
print('Result 1:', result_1)

# Second invocation with different IDs
agent_executor_2 = create_agent_with_params("user789", "haiku012")
result_2 = agent_executor_2.invoke(input)
print('Result 2:', result_2)

# You can also create an agent with just one parameter set
agent_executor_3 = create_agent_with_params("user345", None)
result_3 = agent_executor_3.invoke(input)
print('Result 3:', result_3)