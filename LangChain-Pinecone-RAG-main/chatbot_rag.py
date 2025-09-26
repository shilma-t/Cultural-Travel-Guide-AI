# import streamlit
import streamlit as st
import os
import time
from dotenv import load_dotenv

# import pinecone
from pinecone import Pinecone, ServerlessSpec

# import langchain
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import concurrent.futures

# Load environment variables
load_dotenv()

st.title("Hybrid RAG Chatbot (Groq + Pinecone + Web Search)")

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

# Initialize components
vector_store = get_vector_store()
search_tool = DuckDuckGoSearchRun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        SystemMessage(
            "You are a helpful AI assistant with access to both local documents and current web information."
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
prompt = st.chat_input("Ask me anything...")

if prompt:
    start_time = time.time()
    
    # Add user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))

    # Get documents from Pinecone
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5},
    )
    docs = retriever.invoke(prompt)
    docs_text = "".join(d.page_content for d in docs) if docs else "No relevant local documents found."

    # Get web search results
    try:
        web_results = search_tool.run(prompt)
        web_text = f"Web Search Results: {web_results}"
    except Exception as e:
        web_results = None
        web_text = f"Web search failed: {e}"
        st.warning("Web search encountered an error, continuing with local documents.")

    # Initialize LLM (Groq + supported model)
    try:
        llm = ChatGroq(
            api_key=os.environ.get("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",  # Updated to current supported model
            temperature=0.7
        )
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        st.error("Please check your GROQ_API_KEY and model name")
        st.stop()

    # Create system prompt with contexts
    system_prompt = """You are a helpful AI assistant with access to both local documents and current web information.

    For simple greetings or casual conversation, respond naturally and briefly (1-2 sentences).
    For actual questions or requests for information, use the context below to provide comprehensive answers.
    
    Keep your answers concise and informative.
    
    Local Documents Context: {local_context}
    
    Web Search Context: {web_context}"""

    system_prompt_fmt = system_prompt.format(
        local_context=docs_text,
        web_context=web_text
    )

    print("-- SYS PROMPT --")
    print(system_prompt_fmt)
    print(f"📚 Local docs found: {len(docs) if docs else 0}")
    print(f"🌐 Web search results: {'Yes' if web_results else 'No'}")

    # Add system prompt to message history
    st.session_state.messages.append(SystemMessage(system_prompt_fmt))

    # Invoke the LLM
    try:
        result = llm.invoke(st.session_state.messages).content
    except Exception as e:
        st.error(f"Error calling LLM: {e}")
        st.error("Please check your GROQ_API_KEY and model access")
        st.stop()

    # Add LLM response to chat
    with st.chat_message("assistant"):
        st.markdown(result)
        st.session_state.messages.append(AIMessage(result))
