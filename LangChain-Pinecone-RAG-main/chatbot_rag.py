import streamlit as st
import os
import time
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import concurrent.futures
import requests
import json

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables
load_dotenv()

# Page setup
st.set_page_config(
    page_title="🌍 Cultural Travel Guide",
    page_icon="🌍",
    layout="wide",
)

# ---------------- UI Layer Only ----------------
st.markdown("""
<style>
    /* Background gradient */
    body {
        background: linear-gradient(135deg, #f3f9ff, #fff7f3);
    }

    /* Title */
    h1, h2, h3 {
        font-family: "Trebuchet MS", sans-serif;
        font-weight: bold;
        color: #ff7b54;
    }

    /* Chat bubbles */
    .chat-bubble {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        font-size: 1rem;
        line-height: 1.4;
    }
    .user-bubble {
        background: #DCF8C6;
        margin-left: auto;
        text-align: right;
    }
    .assistant-bubble {
        background: #ffffff;
        border: 1px solid #ddd;
        margin-right: auto;
        text-align: left;
    }

    /* Buttons */
    .stButton>button {
        background: #ff7b54;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #ff9b74;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #eee;
    }

    /* Input box */
    div[data-baseweb="input"] {
        border-radius: 12px !important;
        border: 1px solid #ff7b54 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header (UI only)
st.markdown(
    """
    <div style="text-align:center;">
        <h1>🌍 Cultural Travel Guide</h1>
        <p style="font-size:18px; color:#555;">
        Discover activities, food, and cultural experiences around the world!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
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

def is_travel_domain_query(text: str) -> bool:
    text_l = text.lower()
    activity_terms = [
        "things to do", "activities", "attractions", "landmarks", "places to see",
        "sightseeing", "tour", "tours", "visit", "explore", "museums", "temples",
        "parks", "hiking", "cultural show", "festival", "market", "experience"
    ]
    food_terms = [
        "food", "foods", "dish", "dishes", "cuisine", "eat", "eating", "restaurant",
        "restaurants", "hotel", "hotels", "dine", "dining", "street food", "veg",
        "vegetarian", "vegan", "allergy", "allergies", "gluten", "halal", "kosher",
        "breakfast", "lunch", "dinner", "brunch", "cafe", "café"
    ]
    travel_terms = ["travel", "trip", "destination", "city", "country", "place", "visit"]
    return any(t in text_l for t in activity_terms) or any(t in text_l for t in food_terms) or any(t in text_l for t in travel_terms)

def is_food_domain_query(text: str) -> bool:
    text_l = text.lower()
    food_terms = [
        "food", "foods", "dish", "dishes", "cuisine", "eat", "eating", "restaurant",
        "restaurants", "hotel", "hotels", "dine", "dining", "street food", "veg",
        "vegetarian", "vegan", "allergy", "allergies", "gluten", "halal", "kosher",
        "breakfast", "lunch", "dinner", "brunch", "cafe", "café"
    ]
    travel_terms = ["travel", "trip", "destination", "city", "country", "place", "visit"]
    return any(t in text_l for t in food_terms) or any(t in text_l for t in travel_terms)

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
            dest = m.group(1).strip(" .!?,")
            return dest
    # fallback: look for last capitalized token sequence
    tokens = re.findall(r"[A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+)*", text_stripped)
    if tokens:
        return tokens[-1]
    return None

def extract_preferences(text: str) -> Tuple[Optional[str], bool, List[str]]:
    destination = extract_destination(text)
    tl = text.lower()
    is_veg = False
    if re.search(r"\b(vegetarian|vegan|veg-only|veg friendly|veg-friendly)\b", tl):
        is_veg = True
    if re.search(r"\b(non-veg|non veg|meat lover|steak)\b", tl):
        is_veg = False
    # Extract allergies
    known_allergens = [
        "peanut", "peanuts", "tree nut", "tree nuts", "nut", "nuts", "almond", "cashew", "walnut",
        "pistachio", "hazelnut", "pecan", "macadamia", "brazil nut", "sesame", "soy", "soya",
        "gluten", "wheat", "dairy", "milk", "lactose", "egg", "eggs", "shellfish", "shrimp",
        "prawn", "crab", "lobster", "mollusk", "clam", "oyster", "fish", "mustard"
    ]
    allergies: List[str] = []
    if "allerg" in tl or re.search(r"\bno\s+\w+\b", tl):
        for allergen in known_allergens:
            if re.search(rf"\b{re.escape(allergen)}\b", tl):
                allergies.append(allergen)
    # Normalize unique singular terms
    normalized = []
    for a in allergies:
        a_s = a.rstrip('s')
        if a_s not in normalized:
            normalized.append(a_s)
    return destination, is_veg, normalized

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
            "You are a cultural travel guide that can help with both activities and food recommendations. You: \n"
            "- For activities: discuss attractions, experiences, and things to do in the requested destination.\n"
            "- For food: discuss foods, cuisines, restaurants, and hotels in the requested destination.\n"
            "- If the user says they are vegetarian, recommend only vegetarian-friendly options.\n"
            "- If the user lists allergies, avoid dishes containing those allergens and warn if uncertain.\n"
            "- If the request is unrelated to travel, activities, or food, politely refuse.\n"
            "- Prefer concise bullet lists with 3-6 suggestions per category.\n"
            "- Include a one-line reason why each recommendation is culturally or locally significant.\n"
            "- For activities: categorize under Museums & Culture, Outdoor Activities, Food & Drink, Festivals & Events.\n"
            "- For food: include estimated cost and mention dietary restrictions when relevant."
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
prompt = st.chat_input("Enter a destination and ask for activities or food recommendations...")

if prompt:
    start_time = time.time()
    
    # Add user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))

    # Domain guardrail
    if not is_travel_domain_query(prompt):
        refusal = (
            "I can help with travel recommendations only. Please provide a destination and ask about activities or food."
        )
        with st.chat_message("assistant"):
            st.markdown(refusal)
            st.session_state.messages.append(AIMessage(refusal))
        st.stop()

    # Extract destination and preferences
    destination = extract_destination(prompt)
    if not destination:
        clarify = "Please provide a travel destination (e.g., 'I'm visiting Rome')."
        with st.chat_message("assistant"):
            st.markdown(clarify)
            st.session_state.messages.append(AIMessage(clarify))
        st.stop()

    # Extract food preferences if it's a food query
    is_veg = False
    allergies = []
    if is_food_domain_query(prompt):
        _, is_veg, allergies = extract_preferences(prompt)

    # Get documents from Pinecone
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5}
    )
    
    # Determine search query based on domain
    if is_food_domain_query(prompt):
        search_query = f"popular foods and restaurants in {destination}"
    else:
        search_query = f"popular attractions and activities in {destination}"
    
    docs = retriever.invoke(search_query)
    docs_text = "".join(d.page_content for d in docs) if docs else ""

    # Web search
    try:
        queries = []
        if is_food_domain_query(prompt):
            # Food-related queries
            if is_veg:
                queries.append(f"best vegetarian dishes {destination}")
                queries.append(f"vegetarian friendly restaurants {destination}")
                queries.append(f"vegetarian friendly hotels {destination}")
            else:
                queries.append(f"popular local dishes {destination}")
                queries.append(f"best restaurants {destination}")
                queries.append(f"best hotels for food lovers {destination}")
            if allergies:
                # Seek safe options avoiding allergens
                safe = ", ".join(allergies)
                queries.append(f"allergy friendly restaurants {destination} avoid {safe}")
        else:
            # Activity-related queries
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

    # Create system prompt based on query type
    if is_food_domain_query(prompt):
        system_prompt = f"""You are a cultural travel food guide. STRICT RULES:
        - Scope: Only recommend foods, dishes, restaurants, and food-relevant hotels in the given destination.
        - Vegetarian: If vegetarian=true, only suggest vegetarian or clearly veg-friendly options; label them.
        - Allergies: Avoid dishes containing these allergens: {", ".join(allergies) if allergies else "none"}. If any item is ambiguous, warn and suggest asking staff.
        - Refuse unrelated questions with one sentence.
        - Output format: concise bullet lists with 3-6 items per section. Include a one-line reason for each.

        Destination: {destination}
        Preferences: vegetarian={is_veg}, allergies={", ".join(allergies) if allergies else "none"}

        Local Documents Context:
        {docs_text}

        Web Search Context:
        {web_text}
        """
    else:
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

    # Add system prompt to message history
    st.session_state.messages.append(SystemMessage(system_prompt))

    # Call Groq API
    try:
        if is_food_domain_query(prompt):
            with st.spinner("Finding food recommendations..."):
                result = call_groq_api(st.session_state.messages, groq_api_key)
        else:
            with st.spinner("Finding activities with categories, duration, and cost..."):
                result = call_groq_api(st.session_state.messages, groq_api_key)
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        st.error("Please check your GROQ_API_KEY and model access")
        st.stop()

    # Add LLM response to chat
    with st.chat_message("assistant"):
        st.markdown(result)
        st.session_state.messages.append(AIMessage(result))

