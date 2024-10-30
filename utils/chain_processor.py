# File: utils/chain_processor.py

import streamlit as st
from typing import List, Dict, Any, Union
from utils.my_langchain_tools import *
#from utils.message_handler import store_ai_message

def process_chain_response(response: List[Dict[str, Any]], prompt: str) -> None:
    """
    Process the response from the LangChain generation process and handle
    different tool executions appropriately.
    
    Args:
        response (List[Dict[str, Any]]): The response from generate_query_chain
        prompt (str): The original user prompt
    """
    #print ("I am in process_chain_response, response", response)
    if not isinstance(response, list) or len(response) == 0:
        st.error("Invalid response from chain. Please try again.")
        return
    
    tool_call = response[0]
    
    # Store tool information in session state
    st.session_state.tool_name = tool_call["name"]
    
    print ("tool_call prompt", prompt)

    setup_confirmation_state(tool_call, prompt)


# def requires_confirmation(tool_name: str) -> bool:
#     """
#     Determine if a tool requires query confirmation before execution.
    
#     Args:
#         tool_name (str): Name of the tool
        
#     Returns:
#         bool: True if the tool requires confirmation, False otherwise
#     """
#     confirmation_required_tools = {
#         "SQL_QueryTool",
#         "Graph_QueryTool",
#         "Fulltext_QueryTool",
#         "Vector_QueryTool"
#     }
#     return tool_name in confirmation_required_tools

def setup_confirmation_state(tool_call: Dict[str, Any], prompt: str) -> None:
    """
    Set up the session state for query confirmation.
    
    Args:
        tool_call (Dict[str, Any]): The tool call information
        prompt (str): The original user prompt
    """
    st.session_state.awaiting_confirmation = True
    st.session_state.current_query = tool_call["output"]
    st.session_state.current_chain_input = prompt

# def execute_tool_directly(tool_call: Dict[str, Any], prompt: str) -> None:
#     """
#     Execute a tool that doesn't require confirmation.
    
#     Args:
#         tool_call (Dict[str, Any]): The tool call information
#         prompt (str): The original user prompt
#     """
#     print ("I am in execute_tool_directly")
#     try:
#         query_response = execute_query(prompt, tool_call["output"])
#         process_tool_response(query_response, tool_call)
#     except Exception as e:
#         handle_tool_execution_error(e, tool_call)

# def process_tool_response(
#     query_response: Union[str, Dict[str, Any]], 
#     tool_call: Dict[str, Any]
# ) -> None:
#     """
#     Process the response from a tool execution.
    
#     Args:
#         query_response: The response from the tool
#         tool_call: The original tool call information
#     """
#     try:
#         # Format the response based on tool type
#         formatted_response = format_tool_response(query_response, tool_call)
        
#         # Store the formatted response
#         store_ai_message(formatted_response, tool_call["output"])
        
#     except Exception as e:
#         st.error(f"Error processing tool response: {str(e)}")

# def format_tool_response(
#     response: Union[str, Dict[str, Any]], 
#     tool_call: Dict[str, Any]
# ) -> str:
#     """
#     Format the tool response based on the tool type and response content.
    
#     Args:
#         response: The raw response from the tool
#         tool_call: The tool call information
        
#     Returns:
#         str: Formatted response
#     """
#     tool_name = tool_call["name"]

#     print ("I am in format_tool_response")
    
#     if tool_name == "Vector_QueryTool":
#         return format_vector_tool_response(response)
#     elif tool_name == "Graph_QueryTool":
#         return format_graph_tool_response(response)
#     elif tool_name == "SQL_QueryTool":
#         return format_sql_tool_response(response)
#     elif tool_name == "Fulltext_QueryTool":
#         return format_fulltext_tool_response(response)
#     else:
#         return str(response)

# def format_vector_tool_response(response: Union[str, Dict[str, Any]]) -> str:
#     """Format response from Vector_QueryTool"""
#     if isinstance(response, dict):
#         definitions = response.get('definitions', [])
#         if not definitions:
#             return "No similar definitions found."
            
#         result = "Found similar definitions:\n\n"
#         for def_item in definitions:
#             similarity = def_item.get('similarity', 0)
#             content = def_item.get('content', '')
#             result += f"- [{similarity:.2f}] {content}\n"
#         return result
#     return str(response)

# def format_graph_tool_response(response: Union[str, Dict[str, Any]]) -> str:
#     """Format response from Graph_QueryTool"""
#     if isinstance(response, dict):
#         relationships = response.get('relationships', [])
#         if not relationships:
#             return "No relationships found."
            
#         result = "Found the following relationships:\n\n"
#         for rel in relationships:
#             source = rel.get('source', '')
#             target = rel.get('target', '')
#             rel_type = rel.get('type', '')
#             result += f"- {source} → {rel_type} → {target}\n"
#         return result
#     return str(response)

# def format_sql_tool_response(response: Union[str, Dict[str, Any]]) -> str:
#     """Format response from SQL_QueryTool"""

#     print ("I am in format_sql_tool_response")
#     if isinstance(response, list):
#         if not response:
#             return "No results found."
            
#         # Convert to markdown table
#         headers = response[0].keys()
#         table = "| " + " | ".join(map(str, headers)) + " |\n"
#         table += "|" + "|".join(["---" for _ in headers]) + "|\n"
        
#         for row in response:
#             table += "| " + " | ".join(map(str, [row[h] for h in headers])) + " |\n"
#         return table
#     return str(response)

# def format_fulltext_tool_response(response: Union[str, Dict[str, Any]]) -> str:
#     """Format response from Fulltext_QueryTool"""
#     if isinstance(response, dict):
#         matches = response.get('matches', [])
#         if not matches:
#             return "No matching documents found."
            
#         result = "Found the following matches:\n\n"
#         for match in matches:
#             score = match.get('score', 0)
#             text = match.get('text', '')
#             result += f"- [{score:.2f}] {text}\n"
#         return result
#     return str(response)

# def handle_tool_execution_error(error: Exception, tool_call: Dict[str, Any]) -> None:
#     """
#     Handle errors that occur during tool execution.
    
#     Args:
#         error (Exception): The error that occurred
#         tool_call (Dict[str, Any]): The tool call that caused the error
#     """
#     error_msg = f"Error executing {tool_call['name']}: {str(error)}"
#     st.error(error_msg)
    
#     # Provide tool-specific error handling suggestions
#     if suggestion := get_tool_specific_suggestion(tool_call["name"], str(error)):
#         st.info(f"Suggestion: {suggestion}")

# def get_tool_specific_suggestion(tool_name: str, error_message: str) -> str:
#     """
#     Get tool-specific suggestions for handling errors.
    
#     Args:
#         tool_name (str): Name of the tool
#         error_message (str): The error message
        
#     Returns:
#         str: A suggestion for handling the error
#     """
#     error_lower = error_message.lower()
    
#     suggestions = {
#         "SQL_QueryTool": {
#             "syntax error": "Check the SQL syntax and ensure all columns and tables exist.",
#             "permission denied": "This query may require different permissions.",
#             "relation": "Verify that all table names are correct."
#         },
#         "Graph_QueryTool": {
#             "depth": "Try reducing the number of relationship levels.",
#             "cycle": "Check for circular relationships in the query.",
#             "timeout": "Add more specific filters to reduce the query scope."
#         },
#         "Vector_QueryTool": {
#             "dimension": "Ensure the vector dimensions match (should be 1536).",
#             "invalid": "Check the vector format and normalization."
#         },
#         "Fulltext_QueryTool": {
#             "invalid": "Verify the search syntax and text formatting.",
#             "language": "Check if the text is in the expected language."
#         }
#     }
    
#     tool_suggestions = suggestions.get(tool_name, {})
#     for error_key, suggestion in tool_suggestions.items():
#         if error_key in error_lower:
#             return suggestion
            
#     return "Try rephrasing your question or using a different approach."