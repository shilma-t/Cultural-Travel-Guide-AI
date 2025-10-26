"""
Reusable UI Components for Cultural Travel Guide AI
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import List, Dict, Optional
import time

class UIComponents:
    """Reusable UI components for consistent design across the app"""
    
    @staticmethod
    def header(title: str, subtitle: str, agents: List[Dict[str, str]] = None):
        """Create a beautiful header with animated background"""
        agents_html = ""
        if agents:
            agents_html = '<div class="agent-showcase">'
            for agent in agents:
                agents_html += f'''
                <div class="agent-badge {agent.get('type', 'default')}">
                    {agent.get('icon', '🤖')} {agent.get('name', 'Agent')}
                </div>
                '''
            agents_html += '</div>'
        
        return f"""
        <div class="header-container">
            <h1 class="header-title">{title}</h1>
            <p class="header-subtitle">{subtitle}</p>
            {agents_html}
        </div>
        """
    
    @staticmethod
    def agent_indicator(agent_name: str, agent_type: str = None):
        """Create a styled agent indicator badge"""
        if not agent_type:
            agent_type = agent_name.lower()
        
        return f'<span class="agent-indicator {agent_type}">{agent_name}</span>'
    
    @staticmethod
    def loading_animation(text: str = "Loading..."):
        """Create a loading animation component"""
        return f"""
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">{text}</div>
        </div>
        """
    
    @staticmethod
    def capability_card(title: str, capabilities: List[str]):
        """Create a capability card for agent information"""
        capabilities_html = ""
        for capability in capabilities:
            capabilities_html += f"<li>{capability}</li>"
        
        return f"""
        <div class="capability-card">
            <h4>{title}</h4>
            <ul>
                {capabilities_html}
            </ul>
        </div>
        """
    
    @staticmethod
    def tips_container(tips: List[str]):
        """Create a tips container with helpful information"""
        tips_html = ""
        for tip in tips:
            tips_html += f"<li>{tip}</li>"
        
        return f"""
        <div class="tips-container">
            <h3>💡 Travel Tips</h3>
            <ul>
                {tips_html}
            </ul>
        </div>
        """
    
    @staticmethod
    def sources_container(sources: List[str]):
        """Create a sources container for references"""
        sources_html = ""
        for source in sources:
            sources_html += f"<li>{source}</li>"
        
        return f"""
        <div class="sources-container">
            <h4>Knowledge Sources</h4>
            <ul>
                {sources_html}
            </ul>
        </div>
        """
    
    @staticmethod
    def follow_up_suggestions(suggestions: List[str], message_count: int):
        """Create follow-up suggestion buttons"""
        suggestions_html = ""
        for i, suggestion in enumerate(suggestions):
            suggestions_html += f'''
            <div class="follow-up-suggestion" onclick="window.parent.postMessage({{'type': 'suggestion', 'text': '{suggestion}'}}, '*')">
                {suggestion}
            </div>
            '''
        
        return f"""
        <div class="follow-up-container">
            <h4>💡 Suggested Follow-up Questions</h4>
            {suggestions_html}
        </div>
        """
    
    @staticmethod
    def footer():
        """Create a consistent footer"""
        return """
        <div class="footer-container">
            <p class="footer-text">🌍 Cultural Travel Guide AI | Powered by Multi-Agent Intelligence</p>
            <p class="footer-text" style="margin-top: 0.5rem; font-size: 0.8rem;">Your gateway to authentic cultural experiences worldwide</p>
        </div>
        """
    
    @staticmethod
    def success_message(message: str):
        """Create a success message with animation"""
        return f"""
        <div class="stSuccess">
            ✅ {message}
        </div>
        """
    
    @staticmethod
    def error_message(message: str):
        """Create an error message with styling"""
        return f"""
        <div class="stError">
            ❌ {message}
        </div>
        """
    
    @staticmethod
    def info_message(message: str):
        """Create an info message with styling"""
        return f"""
        <div class="stInfo">
            ℹ️ {message}
        </div>
        """
    
    @staticmethod
    def warning_message(message: str):
        """Create a warning message with styling"""
        return f"""
        <div class="stWarning">
            ⚠️ {message}
        </div>
        """
    
    @staticmethod
    def progress_bar(progress: int, text: str = ""):
        """Create a progress bar with text"""
        return f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%"></div>
            <div class="progress-text">{text}</div>
        </div>
        """
    
    @staticmethod
    def animated_counter(value: int, label: str, duration: int = 1000):
        """Create an animated counter component"""
        return f"""
        <div class="counter-container">
            <div class="counter-value" data-target="{value}">0</div>
            <div class="counter-label">{label}</div>
        </div>
        <script>
            const counter = document.querySelector('.counter-value');
            const target = parseInt(counter.dataset.target);
            const increment = target / {duration};
            let current = 0;
            
            const updateCounter = () => {{
                if (current < target) {{
                    current += increment;
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                }} else {{
                    counter.textContent = target;
                }}
            }};
            
            updateCounter();
        </script>
        """

class AnimationHelper:
    """Helper class for animations and transitions"""
    
    @staticmethod
    def fade_in(element_id: str, duration: int = 500):
        """Add fade-in animation to an element"""
        return f"""
        <script>
            document.getElementById('{element_id}').style.opacity = '0';
            document.getElementById('{element_id}').style.transition = 'opacity {duration}ms ease-in-out';
            setTimeout(() => {{
                document.getElementById('{element_id}').style.opacity = '1';
            }}, 100);
        </script>
        """
    
    @staticmethod
    def slide_in(element_id: str, direction: str = "left", duration: int = 500):
        """Add slide-in animation to an element"""
        return f"""
        <script>
            const element = document.getElementById('{element_id}');
            element.style.transform = 'translateX({direction === "left" ? "-100%" : "100%"})';
            element.style.transition = 'transform {duration}ms ease-out';
            setTimeout(() => {{
                element.style.transform = 'translateX(0)';
            }}, 100);
        </script>
        """
    
    @staticmethod
    def pulse_animation(element_id: str, duration: int = 1000):
        """Add pulse animation to an element"""
        return f"""
        <script>
            const element = document.getElementById('{element_id}');
            element.style.animation = 'pulse {duration}ms ease-in-out infinite';
        </script>
        """

class ResponsiveHelper:
    """Helper class for responsive design utilities"""
    
    @staticmethod
    def mobile_breakpoint():
        """Get mobile breakpoint CSS"""
        return """
        @media (max-width: 768px) {
            .header-title { font-size: 2.5rem; }
            .agent-showcase { flex-direction: column; align-items: center; }
            .agent-badge { width: 100%; justify-content: center; }
            .stChatMessage[data-testid="user-message"] .stChatMessage__content,
            .stChatMessage[data-testid="assistant-message"] .stChatMessage__content {
                max-width: 95%;
            }
            .main .block-container { padding: 0.5rem; }
        }
        """
    
    @staticmethod
    def tablet_breakpoint():
        """Get tablet breakpoint CSS"""
        return """
        @media (max-width: 1024px) and (min-width: 769px) {
            .header-title { font-size: 3rem; }
            .agent-showcase { gap: 0.75rem; }
            .main .block-container { padding: 1rem; }
        }
        """

def apply_global_styles():
    """Apply global styles to the entire app"""
    st.markdown("""
    <style>
        /* Global CSS Variables */
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
        
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700&display=swap');
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-secondary); border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--primary-gradient); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--secondary-gradient); }
        
        /* Animations */
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideInLeft { from { transform: translateX(-100%); } to { transform: translateX(0); } }
        @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        @keyframes float { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-30px) rotate(180deg); } }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Responsive design */
        """ + ResponsiveHelper.mobile_breakpoint() + ResponsiveHelper.tablet_breakpoint() + """
    </style>
    """, unsafe_allow_html=True)
