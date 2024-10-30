import base64
from langchain.schema import HumanMessage, AIMessage

# Tool icons mapping
TOOL_ICONS = {
    "SQL_QueryTool": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
            <rect width="36" height="36" fill="#f0f2f6" rx="5"/>
            <text x="18" y="23" font-family="Arial, sans-serif" font-size="18" 
                  font-weight="bold" fill="#0078D4" text-anchor="middle">
                SQL
            </text>
        </svg>
    """,
    
    "Graph_QueryTool": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
            <rect width="36" height="36" fill="#f0f2f6" rx="5"/>
            <!-- Central node -->
            <circle cx="18" cy="18" r="4" fill="#0078D4"/>
            <!-- Surrounding nodes -->
            <circle cx="8" cy="12" r="4" fill="#0078D4" opacity="0.8"/>
            <circle cx="28" cy="12" r="3.5" fill="#0078D4" opacity="0.9"/>
            <circle cx="7" cy="28" r="3.5" fill="#0078D4" opacity="0.7"/>
            <circle cx="26" cy="26" r="3" fill="#0078D4" opacity="0.85"/>
            <!-- Modified top-right node -->
            <circle cx="23" cy="6" r="3" fill="#0078D4" opacity="0.75"/>
            <!-- Connecting lines -->
            <line x1="18" y1="18" x2="8" y2="12" stroke="#0078D4" stroke-width="1.5"/>
            <line x1="18" y1="18" x2="28" y2="12" stroke="#0078D4" stroke-width="1.5"/>
            <line x1="18" y1="18" x2="7" y2="28" stroke="#0078D4" stroke-width="1.5"/>
            <line x1="18" y1="18" x2="26" y2="26" stroke="#0078D4" stroke-width="1.5"/>
            <!-- Modified connection line -->
            <line x1="28" y1="12" x2="23" y2="6" stroke="#0078D4" stroke-width="1.5"/>
        </svg>
    """,
    
    "Vector_QueryTool": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
            <rect width="36" height="36" fill="#f0f2f6" rx="5"/>
            <!-- Coordinate axes (without arrow tips) -->
            <line x1="8" y1="28" x2="28" y2="28" stroke="#0078D4" stroke-width="1.5"/>
            <line x1="8" y1="28" x2="8" y2="8" stroke="#0078D4" stroke-width="1.5"/>
            
            <!-- Vector arrows -->
            <line x1="8" y1="28" x2="20" y2="10" stroke="#0078D4" stroke-width="2"/>
            <path d="M20 10l-3 0m3 0l0 3" stroke="#0078D4" stroke-width="2" stroke-linecap="round"/>
            
            <line x1="8" y1="28" x2="24" y2="22" stroke="#0078D4" stroke-width="2"/>
            <path d="M24 22l-3 -1m3 1l-1 3" stroke="#0078D4" stroke-width="2" stroke-linecap="round"/>
        </svg>
    """,
    
    "Fulltext_QueryTool": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
            <rect width="36" height="36" fill="#f0f2f6" rx="5"/>
            <!-- Text lines -->
            <line x1="8" y1="10" x2="28" y2="10" stroke="#0078D4" stroke-width="2"/>
            <line x1="8" y1="16" x2="24" y2="16" stroke="#0078D4" stroke-width="2"/>
            <line x1="8" y1="22" x2="20" y2="22" stroke="#0078D4" stroke-width="2"/>
            <!-- Magnifying glass -->
            <circle cx="24" cy="24" r="4" fill="none" stroke="#0078D4" stroke-width="2"/>
            <line x1="27" y1="27" x2="30" y2="30" stroke="#0078D4" stroke-width="2" stroke-linecap="round"/>
        </svg>
    """,
    
    "user": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
            <circle cx="18" cy="12" r="6" fill="#f0f2f6" stroke="#0078D4" stroke-width="2"/>
            <path d="M8 32c0-5.5 4.5-10 10-10s10 4.5 10 10" fill="#f0f2f6" stroke="#0078D4" stroke-width="2"/>
        </svg>
    """,
    
    "default": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
            <circle cx="18" cy="18" r="14" fill="#f0f2f6" stroke="#0078D4" stroke-width="2"/>
            <line x1="18" y1="10" x2="18" y2="26" stroke="#0078D4" stroke-width="2"/>
            <line x1="10" y1="18" x2="26" y2="18" stroke="#0078D4" stroke-width="2"/>
        </svg>
    """
}


# Tool descriptions for tooltips
TOOL_DESCRIPTIONS = {
    "SQL_QueryTool": "For all tables in the DrugDB",
    "Graph_QueryTool": "For the relation-rich drugs, disorders, and MOA data",
    "Vector_QueryTool": "Only for the disorder definitions",
    "Fulltext_QueryTool": "Only for the study titles of clinical trials",
}


def svg_to_base64(svg_string: str) -> str:
    """Convert SVG string to base64 encoded data URL"""
    svg_string = ' '.join(svg_string.split()).strip()
    b64 = base64.b64encode(svg_string.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

def get_tool_icon_and_description(message):
    """Get the appropriate icon and description for a message based on tool used"""
    if isinstance(message, HumanMessage):
        return svg_to_base64(TOOL_ICONS["user"].strip()), None
    elif isinstance(message, AIMessage):
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_name = message.tool_calls[0]["name"]
            return svg_to_base64(TOOL_ICONS.get(tool_name, TOOL_ICONS["default"]).strip()), TOOL_DESCRIPTIONS.get(tool_name)
        return svg_to_base64(TOOL_ICONS["default"].strip()), None
