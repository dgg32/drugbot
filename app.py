# File: app.py

from config import init_session_state, add_button_styles
from ui.chat_display import display_chat_messages
from ui.query_confirmation import create_query_confirmation_ui
from utils.query_generator import generator
from langchain.schema import HumanMessage
import streamlit as st
from utils.my_langchain_tools import *
from utils.error_handler import handle_query_error, clear_error_state, clear_confirmation_state
from utils.message_handler import store_ai_message
from utils.chain_processor import process_chain_response
import my_db_specifics

# Example queries that can be used via buttons
EXAMPLE_QUERIES = []
for x in my_db_specifics.sql_examples:
  x["tool_name"] = "SQL_QueryTool"
  EXAMPLE_QUERIES.append(x)

for x in my_db_specifics.graph_examples:
  x["tool_name"] = "Graph_QueryTool"
  EXAMPLE_QUERIES.append(x)

for x in my_db_specifics.full_text_search_examples:
  x["tool_name"] = "Fulltext_QueryTool"
  EXAMPLE_QUERIES.append(x)

for x in my_db_specifics.vector_search_examples:
  x["tool_name"] = "Vector_QueryTool"
  EXAMPLE_QUERIES.append(x)

def create_example_buttons():
    """Create buttons for example queries in a single column"""
    for idx, example in enumerate(EXAMPLE_QUERIES):
        if st.button(
            example["input"], 
            key=f"example_{idx}",
            use_container_width=True,
        ):
            handle_example_query(example)
            st.rerun()


def handle_example_query(example):
    """Handle when an example query button is clicked"""
    # Add the user's "question" to the chat
    st.session_state.messages.append(HumanMessage(content=example["input"]))
    
    # Set up the confirmation state as if the bot generated this query
    st.session_state.awaiting_confirmation = True
    st.session_state.current_query = example["query"]
    st.session_state.current_chain_input = example["input"]
    st.session_state.tool_name = example["tool_name"]


def process_confirmed_query(query):
    """Process a confirmed query and store the response"""
    with st.spinner("Processing confirmed query..."):
        #print ("I am in process_confirmed_query. curre_chain_input", st.session_state.current_chain_input)
        #print ("query", query)
        query_response = execute_query(
            st.session_state.current_chain_input, 
            query
        )
        store_ai_message(query_response, query)
        clear_confirmation_state()

def handle_confirmation_result(confirmation_result):
    """Handle the result of query confirmation"""
    if confirmation_result == "waiting":
        return False
        
    if confirmation_result is not None:
        try:
            process_confirmed_query(confirmation_result)
            return True
        except Exception as e:
            handle_query_error(e)
            return True
    else:
        st.warning("Query rejected. Please try a different question.")
        clear_error_state()
        return True

def run_chatbot():
    """Main function to run the chatbot interface"""
    # Configure the sidebar
    with st.sidebar:
        st.markdown("### Example queries you can try:")
        create_example_buttons()
    
    # Main chat interface
    st.title("DrugBot 💊")
    
    # Initialize session state
    init_session_state()
    
    # Display chat messages in main area
    display_chat_messages()
    
    # Handle confirmation UI if needed
    if st.session_state.awaiting_confirmation:
        confirmation_result = create_query_confirmation_ui()
        if handle_confirmation_result(confirmation_result):
            st.rerun()
    
    # Create the chat input at the bottom
    if prompt := st.chat_input("What would you like to know about the drugs database?", key="chat_input"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        try:
            with st.spinner("Processing response..."):
                #print ("I am in run_chatbot. prompt", prompt)
                generated_query = generator.invoke(prompt)
                #generated_query = generator.invoke({"input": prompt}).get("output")
                #print ("I am in run_chatbot. generated_query", generated_query)
                process_chain_response(generated_query, prompt)
        except Exception as e:
            st.error(f"Error: {str(e)}")
        st.rerun()



if __name__ == "__main__":
    st.set_page_config(
        page_title="DrugBot",
        page_icon="💊",
        layout="wide",  # Make better use of screen width
        initial_sidebar_state="expanded"  # Start with sidebar visible
    )
    add_button_styles()
    run_chatbot()