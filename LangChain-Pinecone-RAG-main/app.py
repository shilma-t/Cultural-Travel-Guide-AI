import streamlit as st
import requests
import json
import time

# -------------------------
# Configuration
# -------------------------
API_KEY = "716c8936e30e4289421bb54a0cd1318635f0804994699059fa12989c93821059"  # replace with your real key
BASE_URL = "http://localhost:8000"  # adjust if FastAPI runs elsewhere

headers = {"x-api-key": API_KEY}

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Language Agent Chatbot", layout="wide")
st.title("💬 Language Agent - Hybrid RAG Chatbot")

menu = st.sidebar.radio("Choose an endpoint", ["Summary", "NER", "Embeddings", "City Language", "Agent Message", "Health Check"])

# -------------------------
# Summary
# -------------------------
if menu == "Summary":
    st.subheader("Text Summarization")
    text_input = st.text_area("Enter text to summarize")
    max_tokens = st.slider("Max summary tokens", 50, 400, 150)

    if st.button("Summarize"):
        payload = {"text": text_input, "max_summary_tokens": max_tokens}
        resp = requests.post(f"{BASE_URL}/v1/summary", json=payload, headers=headers)
        if resp.status_code == 200:
            st.success(resp.json()["summary"])
        else:
            st.error(resp.json())

# -------------------------
# Named Entity Recognition
# -------------------------
elif menu == "NER":
    st.subheader("Named Entity Recognition (NER)")
    text_input = st.text_area("Enter text for NER")
    if st.button("Extract Entities"):
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
    st.subheader("Generate Text Embedding")
    text_input = st.text_area("Enter text for embeddings")
    if st.button("Generate Embedding"):
        payload = {"text": text_input}
        resp = requests.post(f"{BASE_URL}/v1/embed", json=payload, headers=headers)
        if resp.status_code == 200:
            vector = resp.json()["vector"]
            st.write(f"Vector length: {len(vector)}")
            st.json(vector[:50])  # show first 50 values
        else:
            st.error(resp.json())

# -------------------------
# City → Language
# -------------------------
elif menu == "City Language":
    st.subheader("Get Main Language of a City")
    city_input = st.text_input("Enter a city name")
    if st.button("Get Language"):
        payload = {"city": city_input}
        resp = requests.post(f"{BASE_URL}/v1/city_language", json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            st.success(f"🌍 {data['city']} → 🗣 {data['language']}")
        else:
            st.error(resp.json())

# -------------------------
# Agent Message
# -------------------------
elif menu == "Agent Message":
    st.subheader("Agent-to-Agent Messaging")
    sender = st.text_input("Sender", "frontend")
    recipient = st.text_input("Recipient", "backend")
    message_type = st.selectbox("Message Type", ["request_summary", "request_language", "custom"])

    payload = {}
    if message_type == "request_summary":
        payload["text"] = st.text_area("Payload text")
    elif message_type == "request_language":
        payload["city"] = st.text_input("City for language lookup")
    else:
        payload["info"] = st.text_area("Custom payload (JSON-like)", "test")

    if st.button("Send Message"):
        msg = {
            "sender": sender,
            "recipient": recipient,
            "message_type": message_type,
            "payload": payload,
            "timestamp": time.time()
        }
        resp = requests.post(f"{BASE_URL}/v1/agent_message", json=msg, headers=headers)
        if resp.status_code == 200:
            st.json(resp.json())
        else:
            st.error(resp.json())

# -------------------------
# Health Check
# -------------------------
elif menu == "Health Check":
    st.subheader("API Health Status")
    resp = requests.get(f"{BASE_URL}/health")
    if resp.status_code == 200:
        st.success("API is healthy ✅")
        st.json(resp.json())
    else:
        st.error("API not reachable ❌")
