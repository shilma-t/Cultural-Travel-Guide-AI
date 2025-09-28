import streamlit as st
import os
import time
import re
from typing import Optional
from dotenv import load_dotenv
import concurrent.futures
import requests

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun

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
            dest = m.group(1).strip(" .!,?")
            return dest
    tokens = re.findall(r"[A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+)*", text_stripped)
    if tokens:
        return tokens[-1]
    return None

def call_groq_api(messages: list, api_key: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    groq_messages = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            groq_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            groq_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            groq_messages.append({"role": "assistant", "content": msg.content})
    data = {"model": "llama-3.3-70b-versatile", "messages": groq_messages,
            "temperature": 0.4, "max_tokens": 1000}
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
            "You are a cultural travel guide focused strictly on activity recommendations. "
            "You: \n- Only discuss activities, attractions, experiences, and things to do in the requested destination.\n"
            "- If the request is unrelated to activities or travel, politely refuse.\n"
            "- Prefer concise bullet lists with 3-6 activity suggestions.\n"
            "- Include a one-line reason why each activity is culturally or locally significant.\n"
            "- Include estimated duration (hours) or approximate cost if available.\n"
            "- Categorize activities under: Museums & Culture, Outdoor Activities, Food & Drink, Festivals & Events."
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
prompt = st.chat_input("Enter a destination (e.g., I'm visiting Colombo) and ask for activities...")

if prompt:
    start_time = time.time()
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))

    if not is_activity_domain_query(prompt):
        refusal = "I can help with activity recommendations only. Please provide a destination."
        with st.chat_message("assistant"):
            st.markdown(refusal)
            st.session_state.messages.append(AIMessage(refusal))
        st.stop()

    destination = extract_destination(prompt)
    if not destination:
        clarify = "Please provide a travel destination (e.g., 'I'm visiting Colombo')."
        with st.chat_message("assistant"):
            st.markdown(clarify)
            st.session_state.messages.append(AIMessage(clarify))
        st.stop()

    # Pinecone retriever
    retriever = vector_store.as_retriever(search_type="similarity_score_threshold",
                                         search_kwargs={"k": 3, "score_threshold": 0.5})
    docs = retriever.invoke(f"popular attractions and activities in {destination}")
    docs_text = "".join(d.page_content for d in docs) if docs else ""

    # Web search
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
            except Exception:
                return f"Q: {q}\n( search failed )"

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(run_query, queries))
        web_results = "\n\n".join(results)
        web_text = f"Web Search Results for {destination}:\n{web_results}"
    except Exception as e:
        web_results = None
        web_text = f"Web search failed: {e}"
        st.warning("Web search encountered an error; continuing without it.")

    # Check Groq API key
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in environment variables")
        st.stop()

    # System prompt with categories and duration/cost
    system_prompt = f"""You are a cultural travel activity guide. STRICT RULES:
    - Scope: Only recommend activities, attractions, and experiences in the given destination.
    - Refuse unrelated questions with one sentence.
    - Output format: concise bullet lists with 3-6 items per category.
    - For each activity, include a one-line reason why it is culturally or locally significant.
    - Include estimated duration (hours) or approximate cost if available.
    - Categorize activities under these headings: Museums & Culture, Outdoor Activities, Food & Drink, Festivals & Events.

    Destination: {destination}

    Local Documents Context:
    {docs_text}

    Web Search Context:
    {web_text}
    """
    st.session_state.messages.append(SystemMessage(system_prompt))

    # Call Groq API
    try:
        with st.spinner("Finding activities with categories, duration, and cost..."):
            result = call_groq_api(st.session_state.messages, groq_api_key)
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        st.stop()

    with st.chat_message("assistant"):
        st.markdown(result)
        st.session_state.messages.append(AIMessage(result))
