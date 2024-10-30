import streamlit as st
from ui.icons import TOOL_DESCRIPTIONS, TOOL_ICONS, svg_to_base64


def handle_confirmation_buttons(edited_query: str) -> str | None:
    """
    Handle the confirmation and rejection buttons for query editing.
    
    Args:
        edited_query (str): The potentially edited query from the text area
        
    Returns:
        str | None: Returns either:
            - "waiting" if no button was pressed
            - the edited query if Confirm was pressed
            - None if Reject was pressed
    """
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Confirm"):
            st.session_state.awaiting_confirmation = False
            return edited_query
            
    with col2:
        if st.button("Reject"):
            st.session_state.awaiting_confirmation = False
            st.session_state.last_error = None
            st.session_state.retry_count = 0
            return None
            
    return "waiting"

# The complete create_query_confirmation_ui function would look like this:
def create_query_confirmation_ui() -> str | None:
    """
    Create the query confirmation UI and return the confirmed query.
    
    Returns:
        str | None: Returns either:
            - "waiting" if no button was pressed
            - the confirmed/edited query if Confirm was pressed
            - None if Reject was pressed
    """
    # Get the SVG icon for the current tool
    tool_icon = TOOL_ICONS.get(st.session_state.tool_name, TOOL_ICONS["default"])
    icon_b64 = svg_to_base64(tool_icon.strip())
    description = TOOL_DESCRIPTIONS.get(st.session_state.tool_name, "")
    
    # Create header with SVG icon
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="{icon_b64}" style="width: 30px; height: 30px; background: #f0f2f6; padding: 5px; border-radius: 5px;">
            <h3 style="margin: 0;">This query uses the {st.session_state.tool_name.replace('_', ' ')}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"*{description}*")
    
    # If there was an error in the previous attempt, show it
    if st.session_state.last_error:
        st.error(f"Error in previous query: {st.session_state.last_error}")
        st.markdown("Please fix the query and try again, or reject to move to the next question.")
    
    edited_query = st.text_area(
        "Review and edit the query if needed, press Confirm to proceed:", 
        value=st.session_state.current_query,
        height=150
    )
    
    return handle_confirmation_buttons(edited_query)