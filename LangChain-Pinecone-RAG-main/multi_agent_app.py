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
    page_title=" Cultural Travel Guide AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Modern Sleek UI Design ----------------
st.markdown("""
<style>
    /* Import Modern Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    /* Modern Design System Variables */
    :root {
        /* Consistent 3-Color Scheme */
        --primary-orange: #FF6B35;
        --primary-blue: #1DA1F2;
        --primary-green: #17BF63;
        
        /* Extended Palette */
        --primary-orange-light: #FF8A5B;
        --primary-orange-dark: #E55A2B;
        --primary-blue-light: #4A90E2;
        --primary-blue-dark: #1A8CD8;
        --primary-green-light: #10B981;
        --primary-green-dark: #059669;
        
        /* Neutral Palette */
        --white: #FFFFFF;
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-300: #D1D5DB;
        --gray-400: #9CA3AF;
        --gray-500: #6B7280;
        --gray-600: #4B5563;
        --gray-700: #374151;
        --gray-800: #1F2937;
        --gray-900: #111827;
        
        /* Gradients */
        --hero-gradient: linear-gradient(135deg, var(--primary-orange) 0%, var(--primary-blue) 50%, var(--primary-green) 100%);
        --card-gradient: linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%);
        --glass-gradient: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        
        /* Agent Colors - Using consistent 3-color scheme */
        --culture-color: var(--primary-blue);
        --activity-color: var(--primary-orange);
        --food-color: var(--primary-green);
        --language-color: var(--primary-orange);
        
        /* Shadows */
        --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
        --shadow-xl: 0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04);
        --shadow-2xl: 0 25px 50px rgba(0,0,0,0.15);
        
        /* Border Radius */
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-2xl: 24px;
        --radius-full: 9999px;
        
        /* Spacing */
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
        --space-3xl: 4rem;
    }
    
    /* Global Reset and Base Styles */
    * {
        box-sizing: border-box;
    }
    
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: var(--gray-800);
        background: var(--gray-50);
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><pattern id="cultural-bg" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="2" fill="rgba(255,107,53,0.05)"/><circle cx="20" cy="20" r="1" fill="rgba(29,161,242,0.05)"/><circle cx="80" cy="80" r="1.5" fill="rgba(23,191,99,0.05)"/></pattern></defs><rect width="1000" height="1000" fill="url(%23cultural-bg)"/></svg>');
        background-attachment: fixed;
    }
    
    /* Main Container */
    .main .block-container {
        background: var(--gray-50);
        padding: 0;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stDeployButton { display: none; }
    .stDecoration { display: none; }
    .stApp > div:first-child { padding-top: 0; }
    
    /* Modern Hero Section */
    .hero-section {
        background: var(--hero-gradient);
        min-height: 100vh;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="1000" height="1000" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
        color: white;
        max-width: 800px;
        padding: var(--space-2xl);
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        margin: 0 0 var(--space-lg) 0;
        line-height: 1.1;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.25rem;
        font-weight: 400;
        margin: 0 0 var(--space-2xl) 0;
        opacity: 0.9;
        line-height: 1.6;
    }
    
    .hero-cta {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        background: var(--white);
        color: var(--primary-orange);
        padding: var(--space-md) var(--space-xl);
        border-radius: var(--radius-full);
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: var(--shadow-xl);
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .hero-cta:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-2xl);
        background: var(--gray-50);
    }
    
    /* Agent Showcase Grid */
    .agent-showcase {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--space-lg);
        margin: var(--space-3xl) 0;
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .agent-card {
        background: var(--card-gradient);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        box-shadow: var(--shadow-lg);
        transition: all 0.3s ease;
        border: 1px solid var(--gray-200);
        position: relative;
        overflow: hidden;
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-orange);
    }
    
    .agent-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
    }
    
    .agent-card.culture::before { background: var(--culture-color); }
    .agent-card.activity::before { background: var(--activity-color); }
    .agent-card.food::before { background: var(--food-color); }
    .agent-card.language::before { background: var(--language-color); }
    
    .agent-icon {
        font-size: 2rem;
        margin-bottom: var(--space-md);
    }
    
    .agent-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #000000 !important;
        margin: 0 0 var(--space-sm) 0;
    }
    
    .agent-description {
        color: var(--gray-600);
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Modern Chat Interface */
    .chat-container {
        background: var(--white);
        border-radius: var(--radius-2xl);
        padding: var(--space-2xl);
        box-shadow: var(--shadow-xl);
        border: 1px solid var(--gray-200);
        margin: var(--space-2xl) 0;
        position: relative;
    }
    
    .chat-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--hero-gradient);
    }
    
    /* Modern Message Styling */
    .stChatMessage {
        margin: var(--space-lg) 0;
    }
    
    .stChatMessage[data-testid="user-message"] .stChatMessage__content {
        background: var(--hero-gradient);
        color: white;
        border-radius: var(--radius-xl) var(--radius-xl) var(--radius-md) var(--radius-xl);
        padding: var(--space-lg) var(--space-xl);
        box-shadow: var(--shadow-lg);
        margin-left: auto;
        max-width: 80%;
        border: none;
        position: relative;
    }
    
    .stChatMessage[data-testid="user-message"] .stChatMessage__content::after {
        content: '';
        position: absolute;
        bottom: -8px;
        right: 20px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid var(--primary-orange);
    }
    
    .stChatMessage[data-testid="assistant-message"] .stChatMessage__content {
        background: var(--card-gradient);
        color: var(--gray-800);
        border-radius: var(--radius-xl) var(--radius-xl) var(--radius-xl) var(--radius-md);
        padding: var(--space-xl);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        max-width: 90%;
        position: relative;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stChatMessage__content::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 20px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid var(--gray-200);
    }
    
    /* Modern Agent Indicators */
    .agent-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--space-xs);
        padding: var(--space-xs) var(--space-sm);
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 600;
        margin: var(--space-xs) var(--space-xs) var(--space-xs) 0;
        color: white;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .agent-indicator:hover {
        transform: scale(1.05);
    }
    
    .agent-indicator.culture { 
        background: var(--culture-color);
        box-shadow: 0 2px 8px rgba(29, 161, 242, 0.3);
    }
    .agent-indicator.activity { 
        background: var(--activity-color);
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
    }
    .agent-indicator.food { 
        background: var(--food-color);
        box-shadow: 0 2px 8px rgba(23, 191, 99, 0.3);
    }
    .agent-indicator.language { 
        background: var(--language-color);
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
    }
    
    /* Modern Chat Input */
    .stChatInput > div > div > div > div {
        background: var(--white);
        border-radius: var(--radius-2xl);
        border: 2px solid var(--gray-200);
        box-shadow: var(--shadow-lg);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .stChatInput > div > div > div > div:focus-within {
        border-color: var(--primary-orange);
        box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1), var(--shadow-xl);
        transform: translateY(-2px);
    }
    
    .stChatInput textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 16px !important;
        padding: var(--space-lg) var(--space-xl) !important;
        border: none !important;
        background: transparent !important;
        resize: none !important;
        color: var(--gray-800) !important;
    }
    
    .stChatInput textarea::placeholder {
        color: var(--gray-500) !important;
        font-weight: 400 !important;
    }
    
    .stChatInput button {
        background: var(--hero-gradient) !important;
        border: none !important;
        border-radius: var(--radius-full) !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput button:hover {
        transform: scale(1.05) !important;
        box-shadow: var(--shadow-xl) !important;
    }
    
    /* Modern Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, var(--primary-orange) 0%, var(--primary-blue) 50%, var(--primary-green) 100%);
        border-right: 1px solid var(--gray-200);
        padding: var(--space-2xl);
        box-shadow: var(--shadow-lg);
    }
    
    .sidebar h2 {
        font-family: 'Poppins', sans-serif;
        color: white;
        margin-bottom: var(--space-lg);
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .sidebar h3 {
        font-family: 'Inter', sans-serif;
        color: white;
        margin-bottom: var(--space-md);
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Modern Capability Cards */
    .capability-card {
        background: var(--card-gradient);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        margin-bottom: var(--space-md);
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .capability-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--hero-gradient);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .capability-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-orange);
    }
    
    .capability-card:hover::before {
        transform: scaleX(1);
    }
    
    .capability-card h4 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: var(--gray-900);
        margin: 0 0 var(--space-sm) 0;
        font-size: 1rem;
    }
    
    .capability-card ul {
        margin: 0;
        padding-left: var(--space-md);
    }
    
    .capability-card li {
        font-family: 'Inter', sans-serif;
        color: var(--gray-800);
        font-size: 0.9rem;
        margin-bottom: var(--space-xs);
        line-height: 1.4;
    }
    
    /* Modern Tips Section */
    .tips-container {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(74, 144, 226, 0.05) 100%);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        border: 1px solid rgba(255, 107, 53, 0.2);
        margin-top: var(--space-lg);
        position: relative;
        overflow: hidden;
    }
    
    .tips-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--hero-gradient);
    }
    
    .tips-container h3 {
        font-family: 'Poppins', sans-serif;
        color:white;
        margin-bottom: var(--space-lg);
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .tips-container ul {
        margin: 0;
        padding-left: var(--space-md);
    }
    
    .tips-container li {
        font-family: 'Inter', sans-serif;
        color: white;
        font-size: 0.9rem;
        margin-bottom: var(--space-sm);
        line-height: 1.5;
        position: relative;
    }
    
    .tips-container li::marker {
        color: var(--primary-orange);
    }
    
    /* Modern Sources Container */
    .sources-container {
        background: var(--card-gradient);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        margin-top: var(--space-lg);
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-sm);
    }
    
    .sources-container h4 {
        font-family: 'Poppins', sans-serif;
        color: var(--gray-800);
        margin-bottom: var(--space-md);
        font-size: 1rem;
        font-weight: 600;
    }
    
    .sources-container ul {
        margin: 0;
        padding-left: var(--space-md);
    }
    
    .sources-container li {
        font-family: 'Inter', sans-serif;
        color: var(--gray-600);
        font-size: 0.9rem;
        margin-bottom: var(--space-sm);
        line-height: 1.4;
    }
    
    /* Modern Follow-up Suggestions */
    .follow-up-container {
        margin-top: var(--space-xl);
        padding: var(--space-xl);
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(74, 144, 226, 0.05) 100%);
        border-radius: var(--radius-xl);
        border: 1px solid rgba(255, 107, 53, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .follow-up-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--hero-gradient);
    }
    
    .follow-up-container h4 {
        font-family: 'Poppins', sans-serif;
        color: var(--gray-800);
        margin-bottom: var(--space-lg);
        font-size: 1rem;
        font-weight: 600;
    }
    
    .follow-up-suggestion {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-lg);
        padding: var(--space-md) var(--space-lg);
        margin: var(--space-sm) 0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: var(--gray-700);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    
    .follow-up-suggestion::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--hero-gradient);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .follow-up-suggestion:hover {
        background: var(--hero-gradient);
        color: white;
        transform: translateX(8px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-orange);
    }
    
    .follow-up-suggestion:hover::before {
        transform: scaleX(1);
    }
    
    /* Modern Loading Animations */
    .loading-container {
        display: flex;
        align-items: center;
        gap: var(--space-md);
        padding: var(--space-lg);
        background: var(--card-gradient);
        border-radius: var(--radius-xl);
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .loading-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--hero-gradient);
        animation: loading-bar 2s ease-in-out infinite;
    }
    
    @keyframes loading-bar {
        0%, 100% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
    }
    
    .loading-spinner {
        width: 24px;
        height: 24px;
        border: 3px solid var(--gray-200);
        border-top: 3px solid var(--primary-orange);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        font-family: 'Inter', sans-serif;
        color: var(--gray-600);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Modern Footer */
    .footer-container {
        text-align: center;
        margin-top: var(--space-3xl);
        padding: var(--space-2xl);
        background: var(--card-gradient);
        border-radius: var(--radius-2xl);
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .footer-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--hero-gradient);
    }
    
    .footer-text {
        font-family: 'Inter', sans-serif;
        color: var(--gray-600);
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.5;
    }
    
    /* Modern Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-100);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--hero-gradient);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-orange);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .agent-showcase {
            grid-template-columns: 1fr;
            gap: var(--space-md);
        }
        
        .agent-card {
            padding: var(--space-lg);
        }
        
        .stChatMessage[data-testid="user-message"] .stChatMessage__content,
        .stChatMessage[data-testid="assistant-message"] .stChatMessage__content {
            max-width: 95%;
        }
        
        .main .block-container {
            padding: var(--space-sm);
        }
        
        .hero-content {
            padding: var(--space-lg);
        }
    }
    
    @media (max-width: 480px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .agent-card {
            padding: var(--space-md);
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "coordinator" not in st.session_state:
    st.session_state.coordinator = None

# ---------------- Modern Hero Section ----------------
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <h1 class="hero-title">🌍 Cultural Travel Guide AI</h1>
        <p class="hero-subtitle">Your Personal Multi-Agent Travel Companion</p>
        <button class="hero-cta" onclick="document.querySelector('.stChatInput textarea').focus()">
            🚀 Start Planning Your Trip
        </button>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Agent Showcase Section ----------------
st.markdown("""
<div class="agent-showcase">
    <div class="agent-card culture">
        <div class="agent-icon">🏛️</div>
        <h3 class="agent-title">Culture Expert</h3>
        <p class="agent-description">Traditions, customs, etiquette, and cultural practices</p>
    </div>
    <div class="agent-card activity">
        <div class="agent-icon">🎯</div>
        <h3 class="agent-title">Activity Planner</h3>
        <p class="agent-description">Attractions, tours, experiences, and sightseeing</p>
    </div>
    <div class="agent-card food">
        <div class="agent-icon">🍽️</div>
        <h3 class="agent-title">Food Guide</h3>
        <p class="agent-description">Cuisine, restaurants, dietary preferences, and dining</p>
    </div>
    <div class="agent-card language">
        <div class="agent-icon">🗣️</div>
        <h3 class="agent-title">Language Helper</h3>
        <p class="agent-description">Communication, translations, and language assistance</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Modern Sidebar ----------------
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
    <div style="text-align: center; padding: var(--space-lg); background: var(--card-gradient); border-radius: var(--radius-xl); border: 1px solid var(--gray-200); box-shadow: var(--shadow-sm);">
        <h4 style="margin: 0 0 var(--space-sm) 0; color: var(--gray-800); font-family: 'Poppins', sans-serif; font-weight: 600;">🌟 Quick Actions</h4>
        <p style="margin: 0; color: var(--gray-600); font-size: 0.9rem; font-family: 'Inter', sans-serif; line-height: 1.5;">Try asking about specific destinations, activities, or cultural experiences!</p>
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

# ---------------- Modern Chat Input ----------------
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

# ---------------- Modern Footer ----------------
st.markdown("""
<div class="footer-container">
    <p class="footer-text">🌍 Cultural Travel Guide AI | Powered by Multi-Agent Intelligence</p>
    <p class="footer-text" style="margin-top: var(--space-sm); font-size: 0.8rem;">Your gateway to authentic cultural experiences worldwide</p>
</div>
""", unsafe_allow_html=True)
