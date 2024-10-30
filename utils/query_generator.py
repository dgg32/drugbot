from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from utils.my_langchain_tools import *
from langchain_core.messages import AIMessage

llm = ChatOpenAI(model_name="gpt-4o-mini")
tools = [SQL_QueryTool, Graph_QueryTool, 
         Fulltext_QueryTool, Vector_QueryTool]

## chain as tool chooser
llm_with_tools = llm.bind_tools(tools)
tool_map = {tool.name: tool for tool in tools}

def call_tools(msg: AIMessage) -> Runnable:
    """Tool calling helper that preserves original query"""
    # print ("hello, I am in call_tools", msg)
    tool_calls = msg.tool_calls.copy()

    #print ("tool_call", tool_calls)
    for tool_call in tool_calls:
        print ("tool_call in the for loop", tool_call)
        # print ("tool_call args", tool_call.get("args"), type(tool_call.get("args")))
        if isinstance(tool_call.get("args"), dict):
            tool_call["args"] = {
                "my_question": tool_call.get("args").get("my_question"),
                "original_query": tool_call.get("args").get("original_query", tool_call.get("args").get("my_question")),
                "limit": tool_call.get("args").get("limit", 20)
            }
        print ('tool_call["args"]', tool_call["args"])
        tool_call["output"] = tool_map[tool_call["name"]].invoke(tool_call["args"])
    return tool_calls

generator = llm_with_tools | call_tools


## Not working
# from langchain import hub
# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain_core.prompts import MessagesPlaceholder
# # Construct the tool calling agent

# # prompt = hub.pull("hwchase17/openai-tools-agent")
# # prompt.pretty_print()

# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful assistant. Depending on {input}, combine the query tools bound to you and generate the query. Output only the query and nothing else."),
#         MessagesPlaceholder(variable_name="history", optional=True),
#         ("human","{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad", optional=True),
#     ]
# )


# agent = create_tool_calling_agent(llm, tools, prompt)
# # Create an agent executor by passing in the agent and tools
# generator = AgentExecutor(agent=agent, tools=tools, max_iterations = 2, early_stopping_method = "generate", verbose=True, return_intermediate_steps=True)
