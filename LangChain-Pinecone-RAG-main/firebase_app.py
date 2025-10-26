import streamlit as st 
import pyrebase
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit.components.v1 as components
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

# ---------------- Streamlit UI Configuration ----------------
st.set_page_config(
    page_title="🌍 Cultural Travel Guide AI",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- Header Section ----------------
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🌍 Cultural Travel Guide AI</h1>
    <p class="header-subtitle">Your Personal Multi-Agent Travel Companion</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Authentication Forms ----------------
with st.container():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # ---------------- Sign-Up Section ----------------
    st.markdown('<div class="auth-section">', unsafe_allow_html=True)
    st.markdown("### 🚀 Create Your Account")
    st.markdown("Join thousands of travelers discovering cultures worldwide")
    
    col1, col2 = st.columns(2)
    with col1:
        signup_email = st.text_input(
            "📧 Email Address", 
            key="signup_email",
            placeholder="Enter your email address"
        )
    with col2:
        signup_password = st.text_input(
            "🔒 Password", 
            type="password", 
            key="signup_password",
            placeholder="Create a strong password"
        )
    
    if st.button("✨ Create Account", key="signup_btn"):
        if not signup_email or not signup_password:
            st.warning("⚠️ Please enter both email and password.")
        else:
            with st.spinner("Creating your account..."):
                try:
                    auth.create_user_with_email_and_password(signup_email, signup_password)
                    st.success("🎉 Account created successfully! You can now login.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Sign Up Failed: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ---------------- Divider ----------------
    st.markdown("---")
    
    # ---------------- Login Section ----------------
    st.markdown('<div class="auth-section">', unsafe_allow_html=True)
    st.markdown("### 🔐 Welcome Back")
    st.markdown("Sign in to access your personalized travel guide")
    
    col1, col2 = st.columns(2)
    with col1:
        login_email = st.text_input(
            "📧 Email Address", 
            key="login_email",
            placeholder="Enter your email address"
        )
    with col2:
        login_password = st.text_input(
            "🔒 Password", 
            type="password", 
            key="login_password",
            placeholder="Enter your password"
        )
    
    if st.button("🚀 Sign In", key="login_btn"):
        if not login_email or not login_password:
            st.warning("⚠️ Please enter both email and password.")
        else:
            with st.spinner("Signing you in..."):
                try:
                    user = auth.sign_in_with_email_and_password(login_email, login_password)
                    st.success(f"🎉 Login Successful! Welcome {login_email}")
                    
                    # Show loading animation
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        status_text.text(f"Loading your travel guide... {i+1}%")
                        time.sleep(0.02)
                    
                    # Launch the main app
                    script_path = os.path.join(os.getcwd(), "multi_agent_app.py")
                    subprocess.Popen(["streamlit", "run", script_path])

                    st.info("🌍 Opening your Cultural Travel Guide AI...")
                    time.sleep(2)
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Login Failed: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ---------------- Divider ----------------
    st.markdown("---")
    
    # ---------------- Google Sign-In Section ----------------
    st.markdown('<div class="auth-section">', unsafe_allow_html=True)
    st.markdown("### 🌐 Quick Sign-In")
    st.markdown("Use your Google account for instant access")
    
    if st.button("🔗 Sign in with Google", key="google_btn", help="Click to sign in with your Google account"):
        with st.spinner("Connecting to Google..."):
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    scopes=[
                        'openid',
                        'https://www.googleapis.com/auth/userinfo.email',
                        'https://www.googleapis.com/auth/userinfo.profile'
                    ]
                )
                creds = flow.run_local_server(port=0)
                service = build('oauth2', 'v2', credentials=creds)
                user_info = service.userinfo().get().execute()
                email = user_info['email']

                st.success(f"🎉 Google Sign-In Successful! Welcome {email}")
                
                # Show loading animation
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    status_text.text(f"Loading your travel guide... {i+1}%")
                    time.sleep(0.02)
                
                # Launch main app
                script_path = os.path.join(os.getcwd(), "multi_agent_app.py")
                subprocess.Popen(["streamlit", "run", script_path])
                
                st.info("🌍 Opening your Cultural Travel Guide AI...")
                time.sleep(2)
                st.balloons()

            except Exception as e:
                st.error(f"❌ Google Sign-In failed: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Footer ----------------
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; color: #718096; font-family: 'Poppins', sans-serif;">
    <p style="margin: 0; font-size: 0.9rem;">🌍 Cultural Travel Guide AI | Powered by Multi-Agent Intelligence</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem;">Your gateway to authentic cultural experiences worldwide</p>
</div>
""", unsafe_allow_html=True)
