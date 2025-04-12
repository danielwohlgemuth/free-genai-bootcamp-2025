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

@tool("the_tool")
def the_tool(user_id: Optional[str] = None, haiku_id: Optional[str] = None) -> str:
    """A tool that requires a user ID and haiku ID."""
    return f"Tool call successful with user_id: {user_id}, haiku_id: {haiku_id}"

def create_configurable_tool(base_tool):
    def tool_constructor(**config):
        # Get the original function from the tool
        original_func = base_tool.func
        
        # Create a new function with baked-in parameters
        def configured_function(**kwargs):
            # Merge config with kwargs, with kwargs taking precedence
            merged_args = {**config, **kwargs}
            return original_func(**merged_args)
        
        # Create a new tool based on the original
        return StructuredTool(
            name=base_tool.name,
            description=base_tool.description,
            func=configured_function,
            args_schema=base_tool.args_schema
        )
    
    return tool_constructor

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("placeholder", "{messages}"),
    ("placeholder", "{agent_scratchpad}"),
])

def create_agent_with_params(params):
    # Create a tool with the current parameters
    configurable_tool = create_configurable_tool(the_tool)(**params)
    
    # Create a new agent with this tool
    agent_model = create_tool_calling_agent(model, tools=[configurable_tool], prompt=prompt)
    agent_executor = AgentExecutor(agent=agent_model, tools=[configurable_tool], verbose=True, max_iterations=5)
    
    return agent_executor

# Example usage
messages = [("human", "Hi. What does the tool say?")]

# First invocation with specific IDs
agent_executor_1 = create_agent_with_params({"user_id": "user123", "haiku_id": "haiku456"})
result_1 = agent_executor_1.invoke({"messages": messages})
print('Result 1:', result_1)

# Second invocation with different IDs
agent_executor_2 = create_agent_with_params({"user_id": "user789", "haiku_id": "haiku012"})
result_2 = agent_executor_2.invoke({"messages": messages})
print('Result 2:', result_2)

# You can also create an agent with just one parameter set
agent_executor_3 = create_agent_with_params({"user_id": "user345"})
result_3 = agent_executor_3.invoke({"messages": messages})
print('Result 3:', result_3)