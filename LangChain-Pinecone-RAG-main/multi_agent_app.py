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

# ---------------- Advanced Custom CSS for World-Class UI ----------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700&display=swap');
    
    /* CSS Variables for consistent theming */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --culture-gradient: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
        --activity-gradient: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        --food-gradient: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        --language-gradient: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        
        --text-primary: #2d3748;
        --text-secondary: #4a5568;
        --text-muted: #718096;
        --bg-primary: #f7fafc;
        --bg-secondary: #edf2f7;
        --bg-card: #ffffff;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
        --shadow-xl: 0 20px 40px rgba(0,0,0,0.15);
        
        --border-radius-sm: 8px;
        --border-radius-md: 12px;
        --border-radius-lg: 16px;
        --border-radius-xl: 24px;
    }
    
    /* Global styles */
    .main .block-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
        padding: 1rem;
        max-width: 1200px;
    }
    
    /* Header styling with animated background */
    .header-container {
        text-align: center;
        margin-bottom: 2rem;
        padding: 3rem 2rem;
        background: var(--primary-gradient);
        border-radius: var(--border-radius-xl);
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-xl);
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="travel-pattern" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="2" fill="white" opacity="0.1"/><circle cx="80" cy="80" r="1.5" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="1" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="1" fill="white" opacity="0.1"/><path d="M10,50 Q50,10 90,50" stroke="white" stroke-width="0.5" fill="none" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23travel-pattern)"/></svg>');
        animation: float 30s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-30px) rotate(180deg); }
    }
    
    .header-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
        background: linear-gradient(45deg, #ffffff, #f0f8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .header-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 400;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        letter-spacing: 0.5px;
    }
    
    /* Agent showcase */
    .agent-showcase {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    
    .agent-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: var(--border-radius-lg);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        color: white;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    
    .agent-badge:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }
    
    .agent-badge.culture { background: var(--culture-gradient); }
    .agent-badge.activity { background: var(--activity-gradient); }
    .agent-badge.food { background: var(--food-gradient); }
    .agent-badge.language { background: var(--language-gradient); }
    
    /* Chat interface styling */
    .chat-container {
        background: var(--bg-card);
        border-radius: var(--border-radius-xl);
        padding: 2rem;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }
    
    /* Message styling */
    .stChatMessage {
        margin: 1rem 0;
    }
    
    .stChatMessage[data-testid="user-message"] .stChatMessage__content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: var(--border-radius-lg) var(--border-radius-lg) var(--border-radius-sm) var(--border-radius-lg);
        padding: 1rem 1.5rem;
        box-shadow: var(--shadow-md);
        margin-left: auto;
        max-width: 80%;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stChatMessage__content {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: var(--text-primary);
        border-radius: var(--border-radius-lg) var(--border-radius-lg) var(--border-radius-lg) var(--border-radius-sm);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        max-width: 90%;
        position: relative;
    }
    
    /* Agent indicators in messages */
    .agent-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.75rem;
        border-radius: var(--border-radius-sm);
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem 0.25rem 0.25rem 0;
        color: white;
        box-shadow: var(--shadow-sm);
    }
    
    .agent-indicator.culture { background: var(--culture-gradient); }
    .agent-indicator.activity { background: var(--activity-gradient); }
    .agent-indicator.food { background: var(--food-gradient); }
    .agent-indicator.language { background: var(--language-gradient); }
    
    /* Chat input styling */
    .stChatInput > div > div > div > div {
        background: var(--bg-card);
        border-radius: var(--border-radius-lg);
        border: 2px solid var(--border-color);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .stChatInput > div > div > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }
    
    .stChatInput textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 16px !important;
        padding: 1rem 1.5rem !important;
        border: none !important;
        background: transparent !important;
        resize: none !important;
    }
    
    .stChatInput textarea::placeholder {
        color: var(--text-muted) !important;
        font-weight: 400 !important;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-right: 1px solid var(--border-color);
        padding: 1.5rem;
    }
    
    .sidebar h2 {
        font-family: 'Playfair Display', serif;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    .sidebar h3 {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Capability cards */
    .capability-card {
        background: var(--bg-card);
        border-radius: var(--border-radius-md);
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .capability-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: #667eea;
    }
    
    .capability-card h4 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }
    
    .capability-card ul {
        margin: 0;
        padding-left: 1rem;
    }
    
    .capability-card li {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }
    
    /* Tips section */
    .tips-container {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-radius: var(--border-radius-md);
        padding: 1.5rem;
        border: 1px solid #bbdefb;
        margin-top: 1rem;
    }
    
    .tips-container h3 {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .tips-container ul {
        margin: 0;
        padding-left: 1rem;
    }
    
    .tips-container li {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    /* Sources expander */
    .sources-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: var(--border-radius-md);
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid var(--border-color);
    }
    
    .sources-container h4 {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .sources-container ul {
        margin: 0;
        padding-left: 1rem;
    }
    
    .sources-container li {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    /* Follow-up suggestions */
    .follow-up-container {
        margin-top: 1.5rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        border-radius: var(--border-radius-md);
        border: 1px solid #b3d9ff;
    }
    
    .follow-up-container h4 {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .follow-up-suggestion {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm);
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: var(--text-secondary);
        box-shadow: var(--shadow-sm);
    }
    
    .follow-up-suggestion:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateX(5px);
        box-shadow: var(--shadow-md);
    }
    
    /* Loading animations */
    .loading-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: var(--bg-card);
        border-radius: var(--border-radius-md);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .loading-spinner {
        width: 20px;
        height: 20px;
        border: 3px solid var(--border-color);
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Footer styling */
    .footer-container {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: var(--border-radius-xl);
        border: 1px solid var(--border-color);
    }
    
    .footer-text {
        font-family: 'Inter', sans-serif;
        color: var(--text-muted);
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2.5rem;
        }
        
        .agent-showcase {
            flex-direction: column;
            align-items: center;
        }
        
        .agent-badge {
            width: 100%;
            justify-content: center;
        }
        
        .stChatMessage[data-testid="user-message"] .stChatMessage__content,
        .stChatMessage[data-testid="assistant-message"] .stChatMessage__content {
            max-width: 95%;
        }
        
        .main .block-container {
            padding: 0.5rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-gradient);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-gradient);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "coordinator" not in st.session_state:
    st.session_state.coordinator = None

# ---------------- Enhanced Header Section ----------------
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🌍 Cultural Travel Guide AI</h1>
    <p class="header-subtitle">Your Personal Multi-Agent Travel Companion</p>
    <div class="agent-showcase">
        <div class="agent-badge culture">
            🏛️ Culture Expert
        </div>
        <div class="agent-badge activity">
            🎯 Activity Planner
        </div>
        <div class="agent-badge food">
            🍽️ Food Guide
        </div>
        <div class="agent-badge language">
            🗣️ Language Helper
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Enhanced Sidebar ----------------
with st.sidebar:
    st.markdown("## 🤖 AI Agent Capabilities")
    
    if st.session_state.coordinator:
        capabilities = st.session_state.coordinator.get_agent_capabilities()
        
        for agent_name, capabilities_list in capabilities.items():
            with st.expander(f"**{agent_name.title()} Agent**", expanded=False):
                st.markdown(f"""
                <div class="capability-card">
                    <h4>{agent_name.title()} Specialist</h4>
                    <ul>
                """, unsafe_allow_html=True)
                for capability in capabilities_list:
                    st.markdown(f"<li>{capability}</li>", unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div class="tips-container">
        <h3>💡 Travel Tips</h3>
        <ul>
            <li>Ask about <strong>destinations</strong> and <strong>activities</strong></li>
            <li>Mention <strong>dietary preferences</strong> for food recommendations</li>
            <li>Request <strong>language help</strong> for communication</li>
            <li>Ask about <strong>cultural etiquette</strong> for respectful travel</li>
            <li>Get <strong>local insights</strong> and <strong>hidden gems</strong></li>
            <li>Learn about <strong>cultural customs</strong> and <strong>traditions</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 12px; border: 1px solid #e2e8f0;">
        <h4 style="margin: 0 0 0.5rem 0; color: #2d3748; font-family: 'Inter', sans-serif;">🌟 Quick Actions</h4>
        <p style="margin: 0; color: #4a5568; font-size: 0.9rem; font-family: 'Inter', sans-serif;">Try asking about specific destinations, activities, or cultural experiences!</p>
    </div>
    """, unsafe_allow_html=True)

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

# ---------------- Enhanced Chat Interface ----------------
# Display chat history with improved styling
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show agent indicators for assistant messages
        if message["role"] == "assistant" and "agents_used" in message:
            agents_html = ""
            for agent in message["agents_used"]:
                agents_html += f'<span class="agent-indicator {agent.lower()}">{agent}</span>'
            st.markdown(f"<div style='margin-top: 0.75rem;'>{agents_html}</div>", unsafe_allow_html=True)
            
            # Show sources if available
            if "sources" in message and message["sources"]:
                with st.expander("📚 Sources & References"):
                    st.markdown("""
                    <div class="sources-container">
                        <h4>Knowledge Sources</h4>
                        <ul>
                    """, unsafe_allow_html=True)
                    for source in message["sources"]:
                        st.markdown(f"<li>{source}</li>", unsafe_allow_html=True)
                    st.markdown("</ul></div>", unsafe_allow_html=True)

# ---------------- Enhanced Chat Input ----------------
if prompt := st.chat_input("🌍 Ask about travel destinations, activities, food, culture, or language...", key="chat_input"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response with enhanced loading animation
    with st.chat_message("assistant"):
        # Create loading animation
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown("""
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">🤖 Multi-agent collaboration in progress...</div>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            result = st.session_state.coordinator.coordinate_response(prompt)
            
            # Clear loading animation
            loading_placeholder.empty()
            
            # Display response
            st.markdown(result["response"])
            
            # Show agent indicators with enhanced styling
            agents_html = ""
            for agent in result["agents_used"]:
                agents_html += f'<span class="agent-indicator {agent.lower()}">{agent}</span>'
            st.markdown(f"<div style='margin-top: 0.75rem;'>{agents_html}</div>", unsafe_allow_html=True)
            
            # Show sources if available
            if result["sources"]:
                with st.expander("📚 Sources & References"):
                    st.markdown("""
                    <div class="sources-container">
                        <h4>Knowledge Sources</h4>
                        <ul>
                    """, unsafe_allow_html=True)
                    for source in result["sources"]:
                        st.markdown(f"<li>{source}</li>", unsafe_allow_html=True)
                    st.markdown("</ul></div>", unsafe_allow_html=True)
            
            # Add to session state
            st.session_state.messages.append({
                "role": "assistant", 
                "content": result["response"],
                "agents_used": result["agents_used"],
                "sources": result["sources"]
            })
            
            # Show follow-up suggestions with enhanced styling
            if result.get("collaboration", False):
                suggestions = st.session_state.coordinator.suggest_follow_up_questions(
                    prompt, result["agents_used"]
                )
                
                if suggestions:
                    st.markdown("""
                    <div class="follow-up-container">
                        <h4>💡 Suggested Follow-up Questions</h4>
                    """, unsafe_allow_html=True)
                    
                    for i, suggestion in enumerate(suggestions):
                        if st.button(suggestion, key=f"suggestion_{len(st.session_state.messages)}_{i}", help="Click to ask this question"):
                            st.session_state.messages.append({"role": "user", "content": suggestion})
                            st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            # Clear loading animation
            loading_placeholder.empty()
            
            st.error(f"❌ Error generating response: {e}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I'm sorry, I encountered an error while processing your request. Please try again."
            })

# ---------------- Enhanced Footer ----------------
st.markdown("""
<div class="footer-container">
    <p class="footer-text">🌍 Cultural Travel Guide AI | Powered by Multi-Agent Intelligence</p>
    <p class="footer-text" style="margin-top: 0.5rem; font-size: 0.8rem;">Your gateway to authentic cultural experiences worldwide</p>
</div>
""", unsafe_allow_html=True)
