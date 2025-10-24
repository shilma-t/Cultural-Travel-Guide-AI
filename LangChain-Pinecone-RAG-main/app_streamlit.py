import os
import streamlit as st
from dotenv import load_dotenv
from culture_agent import CultureAgent

load_dotenv()

st.set_page_config(page_title="CultureAgent Chat", page_icon="🌍", layout="wide")

# ChatGPT-like CSS
st.markdown("""
<style>
.main .block-container {padding:1rem;}
.message {padding:1rem;border-radius:0.5rem;margin:0.5rem 0;display:flex;align-items:flex-start;flex-wrap:wrap;}
.user {background-color:#f0f2f6;margin-left:20%;color:#000;}
.agent {background-color:#e8f4fd;margin-right:20%;color:#000;}
.avatar {width:40px;height:40px;border-radius:50%;margin-right:1rem;display:flex;align-items:center;justify-content:center;font-weight:bold;}
.user .avatar {background-color:#007bff;color:white;}
.agent .avatar {background-color:#28a745;color:white;}
.stTextInput > div > div > input {border-radius:25px;padding:0.75rem 1rem;font-size:16px;}
</style>
""", unsafe_allow_html=True)

st.title("🌍 CultureAgent – Cultural Travel Guide")

@st.cache_resource
def get_agent():
    return CultureAgent(
        pinecone_api_key=os.environ.get("PINECONE_API_KEY"),
        pinecone_index_name=os.environ.get("PINECONE_INDEX_NAME"),
        groq_api_key=os.environ.get("GROQ_API_KEY"),
    )

agent = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_last_agent_message():
    """Return the most recent agent response."""
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "agent" and msg["content"].strip():
            return msg["content"]
    return None

def send_message(user_input: str):
    user_input = user_input.strip()
    if not user_input:
        return

    previous_answer = get_last_agent_message()

    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate answer
    result = agent.generate_answer(user_input, previous_answer=previous_answer)
    answer_text = result["answer"]

    # Show sources only for web-retrieved answers
    if result.get("retrieved_from") == "web" and result.get("sources"):
        answer_text += f"\n\n(Source retrieved from web: {', '.join(result['sources'])})"

    st.session_state.messages.append({"role": "agent", "content": answer_text})

# Display chat messages
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "agent"
    st.markdown(
        f"<div class='message {role_class}'><div class='avatar'>{msg['role'][0].upper()}</div>{msg['content']}</div>",
        unsafe_allow_html=True
    )

# Input form
with st.form(key="question_form", clear_on_submit=True):
    user_input = st.text_input(
        "Ask about cultural traditions, etiquette, or travel guidance...",
        placeholder="e.g., What are the wedding traditions in Japan?",
        label_visibility="collapsed"
    )
    submit = st.form_submit_button("Send", type="primary", use_container_width=True)

if submit and user_input:
    send_message(user_input)
    st.rerun()
