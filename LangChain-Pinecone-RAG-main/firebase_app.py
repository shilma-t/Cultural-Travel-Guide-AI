import streamlit as st
import pyrebase
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time
import os

# ---------------- Firebase Configuration ----------------
firebaseConfig = {
    "apiKey": "AIzaSyD1XlfDmJOIef8gaNOEy89sAiyNeLxwi-E",
    "authDomain": "cultural-travel-guide.firebaseapp.com",
    "databaseURL": "",
    "projectId": "cultural-travel-guide",
    "storageBucket": "cultural-travel-guide.firebasestorage.app",
    "messagingSenderId": "387677183519",
    "appId": "1:387677183519:web:23849aab18b54f78eb7f2a"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ---------------- Page Config ----------------
st.set_page_config(
    page_title=" Cultural Travel Guide AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CSS for Modern Sleek UI ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

:root {
    --primary-orange: #FF6B35;
    --hero-gradient: linear-gradient(135deg, #FF6B35 0%, #FF8A5B 50%, #4A90E2 100%);
    --white: #FFFFFF;
    --gray-50: #F9FAFB;
    --gray-200: #E5E7EB;
    --gray-600: #4B5563;
    --radius-2xl: 24px;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --shadow-xl: 0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04);
}

body { font-family: 'Inter', sans-serif; background: var(--gray-50); }
#MainMenu, footer, header { visibility: hidden; }

.hero-section {
    background: var(--hero-gradient);
    min-height: 40vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    text-align: center;
}

.auth-container {
    background: var(--white);
    border-radius: var(--radius-2xl);
    padding: var(--space-xl);
    box-shadow: var(--shadow-xl);
    max-width: 500px;
    margin: var(--space-xl) auto;
    border: 1px solid var(--gray-200);
}

.stTextInput > div > div > input {
    border-radius: 12px;
    padding: 0.75rem 1rem;
    border: 2px solid var(--gray-200);
    transition: all 0.3s;
}
.stTextInput > div > div > input:focus { border-color: var(--primary-orange); }

.stButton > button {
    width: 100%;
    padding: 0.75rem;
    border-radius: 9999px;
    background: var(--hero-gradient);
    color: white;
    font-weight: 600;
    transition: all 0.3s;
}
.stButton > button:hover { transform: translateY(-2px); }

.footer-container {
    text-align: center;
    padding: var(--space-xl);
    margin-top: var(--space-xl);
    background: var(--white);
    border-radius: var(--radius-2xl);
    border: 1px solid var(--gray-200);
    box-shadow: var(--shadow-xl);
}
</style>
""", unsafe_allow_html=True)

# ---------------- Hero Section ----------------
st.markdown("""
<div class="hero-section">
    <div>
        <h1 style="font-family:'Poppins', sans-serif; font-weight:800; font-size:2.5rem;">🌍 Cultural Travel Guide AI</h1>
        <p>Your Personal Multi-Agent Travel Companion</p>
    </div>
</div>
""", unsafe_allow_html=True)





# Form Header
st.markdown("### 🔐 Welcome Back")
st.markdown("Sign in to your account to continue your cultural journey.")

# Single Login Form
with st.form("login_form"):
    email = st.text_input("Email", placeholder="Enter your email address", key="form_email")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="form_password")
    
    # Sign In Button
    submit_login = st.form_submit_button("🚀 Sign In", use_container_width=True)
    
    # Signup link
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <p style="color: var(--gray-600); font-size: 0.9rem;">Don't have an account? 
        <a href="#" style="color: var(--primary-orange); text-decoration: none; font-weight: 600;">Sign up here</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div style="display: flex; align-items: center; margin: 1rem 0; color: var(--gray-400); font-size: 14px;"><div style="flex: 1; height: 1px; background: var(--gray-200);"></div><span style="padding: 0 1rem; background: var(--white);">or</span><div style="flex: 1; height: 1px; background: var(--gray-200);"></div></div>', unsafe_allow_html=True)
    
    # Google Sign-In Button
    if st.form_submit_button("🔗 Continue with Google", key="google_btn", help="Sign in with your Google account"):
        with st.spinner("Connecting to Google..."):
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    scopes=['openid','https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile']
                )
                creds = flow.run_local_server(port=0)
                service = build('oauth2', 'v2', credentials=creds)
                email = service.userinfo().get().execute()['email']
                st.success(f"🎉 Welcome, {email}!")
                
                # Progress animation
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i+1)
                    time.sleep(0.02)
                
                subprocess.Popen(["streamlit", "run", os.path.join(os.getcwd(), "multi_agent_app.py")])
                st.info("🌍 Opening your Cultural Travel Guide AI...")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Google Sign-In failed: {e}")

# Form Processing
if submit_login:
    if not email or not password:
        st.warning("⚠️ Please enter both email and password.")
    else:
        with st.spinner("Signing you in..."):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.success(f"🎉 Welcome back, {email}!")
                
                # Progress animation
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i+1)
                    time.sleep(0.02)
                
                subprocess.Popen(["streamlit", "run", os.path.join(os.getcwd(), "multi_agent_app.py")])
                st.info("🌍 Opening your Cultural Travel Guide AI...")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Login Failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)


