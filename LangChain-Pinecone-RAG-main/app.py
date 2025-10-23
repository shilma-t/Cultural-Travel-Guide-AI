import streamlit as st
import requests
import time

# -------------------------
# Configuration
# -------------------------
API_KEY = "716c8936e30e4289421bb54a0cd1318635f0804994699059fa12989c93821059"  # replace with real key
BASE_URL = "http://localhost:8000"  # adjust if FastAPI runs elsewhere

headers = {"x-api-key": API_KEY}

# -------------------------
# Streamlit UI Setup
# -------------------------
st.set_page_config(page_title="Language Agent Chatbot", layout="wide")
st.markdown("<h1 style='text-align:center'>💬 Language Agent </h1>", unsafe_allow_html=True)
st.write("---")

# -------------------------
# Sidebar Menu
# -------------------------
menu = st.sidebar.radio(
    "Choose a feature",
    ["City/Country → Language (Chat)", "Summary", "NER", "Embeddings", "Agent Message", "Health Check"]
)

# -------------------------
# City/Country → Language Chat (Main Chat Interface)
# -------------------------
if menu == "City/Country → Language (Chat)":
    st.subheader("🌍 City/Country → 🗣 Language Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Enter a city or country name..."):
        st.chat_message("user").markdown(f"**You:** {prompt}")
        st.session_state.messages.append({"role": "user", "content": prompt})

        bot_reply = None
        try:
            payload = {"city": prompt.strip()}
            resp = requests.post(f"{BASE_URL}/v1/city_language", json=payload, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                bot_reply = f"🌍 **{data['city']} → 🗣 {data['language']}**\n\n**Common Phrases:**"
                for k, v in data.get("common_phrases", {}).items():
                    bot_reply += f"\n- {k} → {v}"
            else:
                bot_reply = f"❌ Error: {resp.json()}"
        except Exception as e:
            bot_reply = f"⚠️ Exception: {str(e)}"

        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# -------------------------
# Summary
# -------------------------
elif menu == "Summary":
    st.subheader("📝 Text Summarization")
    text_input = st.text_area("Enter text to summarize", height=200)
    max_tokens = st.slider("Max summary tokens", 50, 400, 150)

    if st.button("Summarize"):
        with st.spinner("Generating summary..."):
            payload = {"text": text_input, "max_summary_tokens": max_tokens}
            resp = requests.post(f"{BASE_URL}/v1/summary", json=payload, headers=headers)
            if resp.status_code == 200:
                st.success("✅ Summary generated")
                st.info(resp.json()["summary"])
            else:
                st.error(resp.json())

# -------------------------
# NER
# -------------------------
elif menu == "NER":
    st.subheader("🔍 Named Entity Recognition (NER)")
    text_input = st.text_area("Enter text for NER", height=200)
    if st.button("Extract Entities"):
        with st.spinner("Extracting entities..."):
            payload = {"text": text_input}
            resp = requests.post(f"{BASE_URL}/v1/ner", json=payload, headers=headers)
            if resp.status_code == 200:
                entities = resp.json()["entities"]
                if entities:
                    st.json(entities)
                else:
                    st.info("No entities found.")
            else:
                st.error(resp.json())

# -------------------------
# Embeddings
# -------------------------
elif menu == "Embeddings":
    st.subheader("📊 Generate Text Embedding")
    text_input = st.text_area("Enter text for embeddings", height=200)
    if st.button("Generate Embedding"):
        with st.spinner("Generating embedding..."):
            payload = {"text": text_input}
            resp = requests.post(f"{BASE_URL}/v1/embed", json=payload, headers=headers)
            if resp.status_code == 200:
                vector = resp.json()["vector"]
                st.write(f"Vector length: {len(vector)}")
                st.json(vector[:50])  # show first 50 values
            else:
                st.error(resp.json())

# -------------------------
# Agent Message
# -------------------------
elif menu == "Agent Message":
    st.subheader("🤖 Agent-to-Agent Messaging")
    sender = st.text_input("Sender", "frontend")
    recipient = st.text_input("Recipient", "backend")
    message_type = st.selectbox("Message Type", ["request_summary", "request_language", "custom"])

    payload = {}
    if message_type == "request_summary":
        payload["text"] = st.text_area("Payload text", height=150)
    elif message_type == "request_language":
        payload["city"] = st.text_input("City for language lookup")
    else:
        payload["info"] = st.text_area("Custom payload (JSON-like)", "test", height=150)

    if st.button("Send Message"):
        msg = {
            "sender": sender,
            "recipient": recipient,
            "message_type": message_type,
            "payload": payload,
            "timestamp": time.time()
        }
        with st.spinner("Sending message..."):
            resp = requests.post(f"{BASE_URL}/v1/agent_message", json=msg, headers=headers)
            if resp.status_code == 200:
                st.success("✅ Message sent")
                st.json(resp.json())
            else:
                st.error(resp.json())

# -------------------------
# Health Check
# -------------------------
elif menu == "Health Check":
    st.subheader("💡 API Health Status")
    with st.spinner("Checking API health..."):
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            st.success("API is healthy ✅")
            st.json(resp.json())
        else:
            st.error("API not reachable ❌")
