import streamlit as st
import os
import time
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from pinecone import Pinecone

from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun
import concurrent.futures
import requests
import json

# Load environment variables
load_dotenv()

st.title("Cultural Travel Activity Guide")

# Cache expensive operations
@st.cache_resource
def get_pinecone_index():
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    return pc.Index(index_name)

@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def get_vector_store():
    index = get_pinecone_index()
    embeddings = get_embeddings()
    return PineconeVectorStore(index=index, embedding=embeddings)

def is_activity_domain_query(text: str) -> bool:
    text_l = text.lower()
    activity_terms = [
        "things to do", "activities", "attractions", "landmarks", "places to see",
        "sightseeing", "tour", "tours", "visit", "explore", "museums", "temples",
        "parks", "hiking", "cultural show", "festival", "market", "experience"
    ]
    travel_terms = ["travel", "trip", "destination", "city", "country", "place", "visit"]
    return any(t in text_l for t in activity_terms) or any(t in text_l for t in travel_terms)


def extract_destination(text: str) -> Optional[str]:
    # Simple heuristics for destination phrases
    patterns = [
        r"in\s+([A-Z][A-Za-z\-\s]+)$",
        r"to\s+([A-Z][A-Za-z\-\s]+)$",
        r"at\s+([A-Z][A-Za-z\-\s]+)$",
        r"(?:go(?:ing)?\s+to|visit(?:ing)?)\s+([A-Z][A-Za-z\-\s]+)",
    ]
    text_stripped = text.strip()
    for pat in patterns:
        m = re.search(pat, text_stripped, flags=re.IGNORECASE)
        if m:
            dest = m.group(1).strip(" .!?,")
            return dest
    # fallback: look for last capitalized token sequence
    tokens = re.findall(r"[A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+)*", text_stripped)
    if tokens:
        return tokens[-1]
    return None


def call_groq_api(messages: list, api_key: str) -> str:
    """Call Groq API directly using requests"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Convert LangChain messages to Groq format
    groq_messages = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            groq_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            groq_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            groq_messages.append({"role": "assistant", "content": msg.content})
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": groq_messages,
        "temperature": 0.4,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Groq API error: {e}")


# Initialize components
vector_store = get_vector_store()
search_tool = DuckDuckGoSearchRun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        SystemMessage(
            "You are a cultural travel guide focused strictly on activity recommendations. You: \n"
            "- Only discuss activities, attractions, experiences, and things to do in the requested destination.\n"
            "- If the request is unrelated to activities or travel, politely refuse.\n"
            "- Prefer concise bullet lists with 3-6 activity suggestions.\n"
            "- Include a one-line reason why each activity is culturally or locally significant."
        )
    )

# Display chat messages from history
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Chat input
prompt = st.chat_input("Enter a destination (e.g., Tokyo) and ask for activities...")

if prompt:
    start_time = time.time()
    
    # Add user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))

    # Domain guardrail
    if not is_activity_domain_query(prompt):
        refusal = (
            "I can help with activity recommendations only. Please provide a destination."
        )
        with st.chat_message("assistant"):
            st.markdown(refusal)
            st.session_state.messages.append(AIMessage(refusal))
        st.stop()

    destination = extract_destination(prompt)
    if not destination:
        clarify = "Please provide a travel destination (e.g., 'I'm visiting Rome')."
        with st.chat_message("assistant"):
            st.markdown(clarify)
            st.session_state.messages.append(AIMessage(clarify))
        st.stop()

    # Get documents from Pinecone (optional, may be empty)
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5},
    )
    docs = retriever.invoke(f"popular attractions and activities in {destination}")
    docs_text = "".join(d.page_content for d in docs) if docs else ""

    # Get web search results
    try:
        queries = [
            f"best activities {destination}",
            f"top attractions {destination}",
            f"things to do {destination}",
            f"unique cultural experiences {destination}"
        ]

        def run_query(q: str) -> str:
            try:
                return f"Q: {q}\n{search_tool.run(q)}"
            except Exception as _e:
                return f"Q: {q}\n( search failed )"

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(run_query, queries))
        web_results = "\n\n".join(results)
        web_text = f"Web Search Results for {destination}:\n{web_results}"
    except Exception as e:
        web_results = None
        web_text = f"Web search failed: {e}"
        st.warning("Web search encountered an error; continuing without it.")

    # Check for Groq API key
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in environment variables")
        st.error("Please set your GROQ_API_KEY in the .env file")
        st.stop()

    # Create system prompt with contexts
    system_prompt = """You are a cultural travel activity guide. STRICT RULES:
    - Scope: Only recommend activities, attractions, and experiences in the given destination.
    - Refuse unrelated questions with one sentence.
    - Output format: concise bullet lists with 3-6 items per section. Include a one-line reason for each.

    Destination: {destination}

    Local Documents Context:
    {local_context}

    Web Search Context:
    {web_context}
    """

    system_prompt_fmt = system_prompt.format(
        destination=destination,
        local_context=docs_text or "",
        web_context=web_text or ""
    )

    print("-- SYS PROMPT --")
    print(system_prompt_fmt)
    print(f"📚 Local docs found: {len(docs) if docs else 0}")
    print(f"🌐 Web search results: {'Yes' if web_results else 'No'}")

    # Add system prompt to message history
    st.session_state.messages.append(SystemMessage(system_prompt_fmt))

    # Call Groq API directly
    try:
        result = call_groq_api(st.session_state.messages, groq_api_key)
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        st.error("Please check your GROQ_API_KEY and model access")
        st.stop()

    # Add LLM response to chat
    with st.chat_message("assistant"):
        st.markdown(result)
        st.session_state.messages.append(AIMessage(result))
