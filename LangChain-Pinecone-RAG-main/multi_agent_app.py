"""
Multi-Agent Travel Guide - Unified Streamlit Interface
"""

import os
import streamlit as st
from dotenv import load_dotenv
from agents import AgentCoordinator

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🌍 Multi-Agent Travel Guide",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #ff7b54;
        --secondary-color: #4a90e2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --light-bg: #f8f9fa;
        --dark-text: #2c3e50;
    }

    /* Background gradient */
    .main .block-container {
        background: linear-gradient(135deg, #f3f9ff 0%, #fff7f3 100%);
        padding: 2rem;
    }

    /* Title styling */
    h1 {
        font-family: "Trebuchet MS", sans-serif;
        font-weight: bold;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Chat message styling */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 85%;
        font-size: 1rem;
        line-height: 1.5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .user-message {
        background: linear-gradient(135deg, #DCF8C6 0%, #C8E6C9 100%);
        margin-left: auto;
        text-align: right;
        border: 1px solid #4CAF50;
    }

    .assistant-message {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        margin-right: auto;
        text-align: left;
        border: 1px solid #e0e0e0;
    }

    /* Agent indicators */
    .agent-indicator {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.25rem 0.25rem 0.25rem 0;
        color: white;
    }

    .culture-agent { background-color: #9b59b6; }
    .activity-agent { background-color: #3498db; }
    .food-agent { background-color: #e74c3c; }
    .language-agent { background-color: #f39c12; }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #fafafa;
        border-right: 1px solid #eee;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        padding: 0.75rem 1rem !important;
        font-size: 16px !important;
        border: 2px solid var(--primary-color) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--secondary-color) !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, #ff9b74 100%);
        color: white;
        font-weight: bold;
        border-radius: 25px;
        padding: 0.6rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Follow-up suggestions */
    .follow-up-suggestion {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border: 1px solid #bbdefb;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .follow-up-suggestion:hover {
        background: linear-gradient(135deg, #bbdefb 0%, #e1bee7 100%);
        transform: translateX(5px);
    }

    /* Loading animation */
    .loading-dots {
        display: inline-block;
    }

    .loading-dots::after {
        content: '';
        animation: dots 1.5s steps(4, end) infinite;
    }

    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .chat-message {
            max-width: 95%;
            padding: 0.75rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "coordinator" not in st.session_state:
    st.session_state.coordinator = None

# Header
st.markdown("""
<div>
    <h1>🌍 Multi-Agent Travel Guide</h1>
    <p class="subtitle">
        Get comprehensive travel assistance from specialized AI agents:<br>
        <span class="agent-indicator culture-agent">Culture</span>
        <span class="agent-indicator activity-agent">Activity</span>
        <span class="agent-indicator food-agent">Food</span>
        <span class="agent-indicator language-agent">Language</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with agent information
with st.sidebar:
    st.markdown("## 🤖 Agent Capabilities")
    
    if st.session_state.coordinator:
        capabilities = st.session_state.coordinator.get_agent_capabilities()
        
        for agent_name, capabilities_list in capabilities.items():
            with st.expander(f"**{agent_name.title()} Agent**", expanded=False):
                for capability in capabilities_list:
                    st.write(f"• {capability}")
    
    st.markdown("---")
    st.markdown("## 💡 Tips")
    st.markdown("""
    - Ask about **destinations** and **activities**
    - Mention **dietary preferences** for food recommendations
    - Request **language help** for communication
    - Ask about **cultural etiquette** for respectful travel
    """)

# Initialize coordinator
@st.cache_resource
def get_coordinator():
    try:
        return AgentCoordinator(
            pinecone_api_key=os.environ.get("PINECONE_API_KEY"),
            pinecone_index_name=os.environ.get("PINECONE_INDEX_NAME"),
            groq_api_key=os.environ.get("GROQ_API_KEY"),
        )
    except Exception as e:
        st.error(f"Failed to initialize agents: {e}")
        return None

if st.session_state.coordinator is None:
    with st.spinner("Initializing AI agents..."):
        st.session_state.coordinator = get_coordinator()

if st.session_state.coordinator is None:
    st.error("""
    **Configuration Error**
    
    Please ensure you have set the following environment variables:
    - `PINECONE_API_KEY`
    - `PINECONE_INDEX_NAME` 
    - `GROQ_API_KEY`
    
    Create a `.env` file in your project root with these values.
    """)
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show agent indicators for assistant messages
        if message["role"] == "assistant" and "agents_used" in message:
            agents_html = ""
            for agent in message["agents_used"]:
                agents_html += f'<span class="agent-indicator {agent.lower()}-agent">{agent}</span>'
            st.markdown(f"<div style='margin-top: 0.5rem;'>{agents_html}</div>", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask about travel destinations, activities, food, culture, or language..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🤖 Multi-agent collaboration in progress..."):
            try:
                result = st.session_state.coordinator.coordinate_response(prompt)
                
                # Display response
                st.markdown(result["response"])
                
                # Show agent indicators
                agents_html = ""
                for agent in result["agents_used"]:
                    agents_html += f'<span class="agent-indicator {agent.lower()}-agent">{agent}</span>'
                st.markdown(f"<div style='margin-top: 0.5rem;'>{agents_html}</div>", unsafe_allow_html=True)
                
                # Show sources if available
                if result["sources"]:
                    with st.expander("📚 Sources"):
                        for source in result["sources"]:
                            st.write(f"• {source}")
                
                # Add to session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result["response"],
                    "agents_used": result["agents_used"],
                    "sources": result["sources"]
                })
                
                # Show follow-up suggestions
                if result["collaboration"]:
                    suggestions = st.session_state.coordinator.suggest_follow_up_questions(
                        prompt, result["agents_used"]
                    )
                    
                    if suggestions:
                        st.markdown("**💡 Suggested follow-up questions:**")
                        for suggestion in suggestions:
                            if st.button(suggestion, key=f"suggestion_{len(st.session_state.messages)}"):
                                st.session_state.messages.append({"role": "user", "content": suggestion})
                                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating response: {e}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I'm sorry, I encountered an error while processing your request. Please try again."
                })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    🌍 Multi-Agent Travel Guide | Powered by specialized AI agents for comprehensive travel assistance
</div>
""", unsafe_allow_html=True)
