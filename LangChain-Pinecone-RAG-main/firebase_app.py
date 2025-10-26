import streamlit as st
import pyrebase
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import streamlit as st
import subprocess
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

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Cultural Travel Guide", layout="centered")
st.title("🌏 Cultural Travel Guide")
st.write("Firebase Authentication Demo - Email/Password Login & Google Sign-In")

# ---------------- Sign-Up Section ----------------
st.subheader("Sign Up")
signup_email = st.text_input("Sign Up Email", key="signup_email")
signup_password = st.text_input("Sign Up Password", type="password", key="signup_password")

if st.button("Sign Up"):
    if not signup_email or not signup_password:
        st.warning("Please enter email and password.")
    else:
        try:
            auth.create_user_with_email_and_password(signup_email, signup_password)
            st.success("Account created successfully! You can now login.")
        except Exception as e:
            st.error(f"Sign Up Failed: {e}")

# ---------------- Login Section ----------------
st.subheader("Login")
login_email = st.text_input("Email")
login_password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        user = auth.sign_in_with_email_and_password(login_email, login_password)
        st.success(f"Login Successful! Welcome {login_email}")

        # Launch the other Streamlit app
        script_path = os.path.join(os.getcwd(), "multi_agent_app.py")
        subprocess.Popen(["streamlit", "run", script_path])

        st.info("Opening the main app in a new tab...")
    except Exception as e:
        st.error(f"Login Failed: {e}")

# ---------------- Google Sign-In ----------------
st.subheader("Or Login with Google")
if st.button("Sign in with Google"):
    try:
        # Use credentials.json from Google Cloud OAuth Desktop App
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

        st.success(f"Google Sign-In Successful! Welcome {email}")
        # Launch main app
        script_path = r"C:\Users\shafr\Desktop\Uni\Y3S2\IRWA\IRWA-Cultural TravelGuide\IRWA-Cultural-Travel-Guide-AI\LangChain-Pinecone-RAG-main\multi_agent_app.py"
        subprocess.Popen(["python", script_path])

    except Exception as e:
        st.error(f"Google Sign-In failed:\n{e}")
