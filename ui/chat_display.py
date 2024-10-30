# File: ui/chat_display.py

import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from ui.icons import get_tool_icon_and_description

def display_user_message(message: HumanMessage) -> None:
    """
    Display a user message in the chat interface with appropriate styling and icon.
    
    Args:
        message (HumanMessage): The user's message to display
    """
    # Get the user icon and description (description will be None for user messages)
    icon, _ = get_tool_icon_and_description(message)
    
    # Display the message using Streamlit's chat message component
    with st.chat_message("user", avatar=icon):
        st.markdown(message.content)

def display_assistant_message(message: AIMessage) -> None:
    """
    Display an assistant message in the chat interface with appropriate styling,
    icon, and any tool information.
    
    Args:
        message (AIMessage): The assistant's message to display
    """
    # Get tool information if it exists
    tool_name = (message.tool_calls[0]["name"] 
                if hasattr(message, 'tool_calls') and message.tool_calls 
                else "default")
    
    # Get the icon and description for the tool used
    icon, description = get_tool_icon_and_description(message)
    
    # Display the message using Streamlit's chat message component
    with st.chat_message("assistant", avatar=icon):
        # Display the main message content
        st.markdown(message.content)
        
        # If there are tool calls, show the query details in an expander
        if hasattr(message, 'tool_calls') and message.tool_calls:
            with st.expander("See query details"):
                st.markdown(f"**Tool Used:** {tool_name.replace('_', ' ')}")
                if description:
                    st.markdown(f"**Description:** {description}")
                
                # Display the query if it exists
                if 'args' in message.tool_calls[0]:
                    args = message.tool_calls[0]['args']
                    query = None
                    
                    # Extract query from args
                    if isinstance(args, dict):
                        query = (args.get('executed_query') or 
                               args.get('query') or 
                               args.get('my_question'))
                    elif isinstance(args, str):
                        query = args
                    
                    if query:
                        # Special handling for Vector queries
                        if tool_name == "Vector_QueryTool":
                            display_vector_query(query)
                        else:
                            st.markdown("**Query Used:**")
                            st.code(query, language='sql')

def display_vector_query(query: str) -> None:
    """
    Display a vector query with appropriate formatting and explanation.
    
    Args:
        query (str): The vector query to display
    """
    st.markdown("**⚠️ Truncated Query:**")
    st.markdown("""
    > **Note:** The query below is a simplified version where the embedding vector has been 
    replaced with `{...embedding...}` for readability. To use this query, you would need to 
    replace the placeholder with an actual 1536-dimensional vector.
    """)
    
    # Simplify the vector representation in the query
    import re
    simplified_query = re.sub(
        r'array_distance\(definitionEmbedding,\s*\[.*?\]::FLOAT\[1536\]',
        'array_distance(definitionEmbedding, {...embedding...}::FLOAT[1536]',
        query,
        flags=re.DOTALL
    )
    
    st.code(simplified_query, language='sql')

def display_message_pair(messages: list, i: int) -> bool:
    """
    Display a pair of user and assistant messages, if they exist.
    
    Args:
        messages (list): List of all messages
        i (int): Current index in the message list
        
    Returns:
        bool: True if an assistant message was displayed after the user message
    """
    if isinstance(messages[i], HumanMessage):
        display_user_message(messages[i])
    
    if i + 1 < len(messages) and isinstance(messages[i + 1], AIMessage):
        display_assistant_message(messages[i + 1])
        return True
    return False

def display_chat_messages() -> None:
    """
    Display all chat messages with appropriate styling and separation.
    """
    messages = st.session_state.messages
    i = 0
    while i < len(messages):
        # Display the current message pair
        assistant_displayed = display_message_pair(messages, i)
        
        # Add separator if not the last message
        if i + (2 if assistant_displayed else 1) < len(messages):
            st.markdown('<hr class="qa-separator">', unsafe_allow_html=True)
        
        # Skip the assistant message if we displayed it
        i += 2 if assistant_displayed else 1

