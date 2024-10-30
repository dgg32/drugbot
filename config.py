import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    session_vars = {
        "messages": [],
        "awaiting_confirmation": False,
        "current_query": None,
        "current_chain_input": None,
        "tool_name": None,
        "last_error": None,
        "retry_count": 0
    }
    
    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

def add_svg_styles():
    st.markdown("""
        <style>
        /* Existing styles... */

        /* Remove extra spacing from chat containers */
        [data-testid="stChatMessageContent"] > div:first-child {
            margin-top: 0 !important;
        }
        
        /* Adjust chat message spacing */
        [data-testid="stChatMessage"] {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        /* Add space between Q&A rounds */
        .qa-separator {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #0078D4, transparent);
            margin: 2rem 0;
            opacity: 0.2;
        }

        /* Message container styling */
        [data-testid="stChatMessage"] {
            line-height: 1.5;
        }
        
        /* User message specific styling */
        [data-testid="stChatMessage"][data-test="user"] {
            border-left: 3px solid #0078D4;
        }
        
        /* Assistant message specific styling */
        [data-testid="stChatMessage"][data-test="assistant"] {
            border-left: 3px solid #00a67e;
        }
        
        /* Query confirmation UI styles */
        [data-testid="stMarkdownContainer"] > div {
            margin-bottom: 1rem;
        }
        
        [data-testid="stMarkdownContainer"] img {
            display: inline-block;
            vertical-align: middle;
        }
        
        /* Heading styles next to icon */
        [data-testid="stMarkdownContainer"] h3 {
            display: inline-block;
            vertical-align: middle;
            color: #0078D4;
            font-weight: 600;
            font-size: 1.2rem;
            margin: 0;
            padding: 0;
        }
        
        /* Tool description styles */
        [data-testid="stMarkdownContainer"] em {
            color: #666;
            display: block;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Query text area styles */
        .stTextArea textarea {
            font-family: monospace;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        
        /* Button styles */
        .stButton button {
            width: 100%;
            font-weight: 500;
        }
        
        /* Expander styles for query details */
        .streamlit-expanderHeader {
            font-size: 0.9rem;
            color: #0078D4;
            padding: 0.5rem 0;
        }
        
        /* Code block styles */
        .stCodeBlock {
            margin-top: 0.5rem;
            border-radius: 5px;
        }
        
        /* Legend panel styles */
        [data-testid="stSidebarUserContent"] {
            padding: 1rem;
        }
        
        /* Make column layout more compact */
        [data-testid="column"] {
            padding: 0 0.5rem;
        }
        
        /* Tool legend title */
        [data-testid="stMarkdownContainer"] h3 {
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #0078D4;
        }
        
        /* Error message styling */
        .stAlert {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 5px;
        }
        
        /* Blockquote styling for warnings/notes */
        blockquote {
            border-left: 3px solid #0078D4;
            margin: 1rem 0;
            padding-left: 1rem;
            color: #666;
        }
        
        /* Tool details in expander */
        .streamlit-expander {
            border: 1px solid #eaecef;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        
        /* Spinner/loading indicator */
        .stSpinner {
            text-align: center;
            margin: 1rem 0;
        }
        
        /* Chat input container */
        .stChatInputContainer {
            padding-top: 1rem;
            border-top: 1px solid #eee;
        }
        
        /* Make the chat more readable */
        [data-testid="stChatMessage"] p {
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        
        /* Add subtle hover effect to expandable sections */
        .streamlit-expander:hover {
            background: #f8f9fa;
        }
        
        /* Style the confirmation buttons */
        .stButton button:hover {
            border-color: #0078D4;
        }
        
        /* Add spacing after tool descriptions */
        .tool-description {
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }
        
        /* Make code more readable */
        code {
            font-family: 'Consolas', 'Monaco', monospace;
            background: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 85%;
        }
        </style>
    """, unsafe_allow_html=True)

def add_button_styles():
    """Add custom CSS styles to the interface"""
    st.markdown("""
        <style>
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            padding: 1rem;
        }
        
        /* Sidebar header */
        [data-testid="stSidebar"] [data-testid="stMarkdown"] > h3 {
            color: #0078D4;
            font-size: 1rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #dee2e6;
        }
        
        /* Example query buttons styling */
        [data-testid="stSidebar"] .stButton > button {
            height: auto !important;
            white-space: normal !important;
            text-align: left !important;
            padding: 0.75rem 1rem !important;
            background-color: white !important;
            border: 1px solid #dee2e6 !important;
            margin-bottom: 0.5rem !important;
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
            color: #0078D4 !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #e9ecef !important;
            border-color: #0078D4 !important;
            transform: translateX(3px) !important;
        }
        
        /* Add icon to example queries */
        [data-testid="stSidebar"] .stButton > button::before {
            content: "💡";
            margin-right: 0.5rem;
        }
        
        /* Chat input styling */
        .stChatFloatingInputContainer {
            position: fixed !important;
            bottom: 0 !important;
            left: inherit !important;
            right: 0 !important;
            background: white !important;
            padding: 1rem !important;
            z-index: 999 !important;
            border-top: 1px solid #dee2e6 !important;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1) !important;
        }
        
        /* Ensure chat messages are scrollable and don't go behind input */
        section[data-testid="stSidebar"] + div {
            height: calc(100vh - 100px) !important;
            overflow-y: auto !important;
            padding-bottom: 100px !important;
        }
        
        /* Add hover effect to example buttons */
        [data-testid="stSidebar"] .stButton > button {
            position: relative !important;
        }
        
        [data-testid="stSidebar"] .stButton > button::after {
            content: "→";
            position: absolute;
            right: 1rem;
            opacity: 0;
            transition: all 0.2s ease;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover::after {
            opacity: 1;
            right: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)