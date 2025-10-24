# Multi-Agent Travel Guide AI System

A sophisticated multi-agentic AI system that provides comprehensive travel assistance through specialized AI agents working in collaboration.

## 🤖 Agent Architecture

### Specialized Agents
- **Culture Agent** - Traditions, customs, etiquette, festivals, and cultural practices
- **Activity Agent** - Attractions, tours, experiences, and sightseeing recommendations  
- **Food Agent** - Cuisine, restaurants, dietary preferences, and food experiences
- **Language Agent** - Communication help, translations, and language assistance

### Agent Coordinator
- **Intelligent Routing** - Automatically determines which agents are needed for each query
- **Multi-Agent Collaboration** - Coordinates multiple agents for comprehensive responses
- **Context Sharing** - Enables agents to build upon each other's knowledge

## 🚀 Features

### Smart Query Processing
- Automatically detects query intent and routes to appropriate agents
- Supports multi-domain queries requiring agent collaboration
- Context-aware responses based on destination and preferences

### Specialized Expertise
- **Culture**: Social etiquette, traditions, festivals, cultural sensitivities
- **Activity**: Attractions, tours, outdoor activities, family-friendly options
- **Food**: Local cuisine, dietary restrictions, restaurant recommendations
- **Language**: Essential phrases, pronunciation, communication tips

### Advanced Capabilities
- Dietary preference handling (vegetarian, vegan, allergies)
- Budget-conscious recommendations
- Cultural sensitivity and respect
- Real-time web search integration
- Vector-based knowledge retrieval

## 📁 Project Structure

```
LangChain-Pinecone-RAG-main/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base class for all agents
│   ├── culture_agent.py       # Cultural traditions & etiquette
│   ├── activity_agent.py      # Activities & attractions
│   ├── food_agent.py          # Food & dining
│   ├── language_agent.py      # Language & communication
│   └── coordinator.py         # Agent orchestration
├── documents/                 # Knowledge base PDFs
├── multi_agent_app.py         # Main Streamlit application
├── ingestion.py               # Document processing pipeline
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Pinecone account and API key
- Groq API key

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=your_index_name
   GROQ_API_KEY=your_groq_api_key
   ```

4. Process documents (first time only):
   ```bash
   python ingestion.py
   ```

5. Run the application:
   ```bash
   streamlit run multi_agent_app.py
   ```

## 💡 Usage Examples

### Single Agent Queries
- **Culture**: "What are the wedding traditions in Japan?"
- **Activity**: "What are the best museums to visit in Paris?"
- **Food**: "What vegetarian dishes should I try in India?"
- **Language**: "How do I say 'thank you' in Thai?"

### Multi-Agent Collaboration
- **Planning**: "Plan a 3-day cultural trip to Kyoto"
- **Comprehensive**: "I'm visiting Rome, what should I know about food, culture, and activities?"
- **Specific**: "Help me with language and cultural etiquette for visiting temples in Thailand"

## 🔧 Technical Details

### Technology Stack
- **LLM**: Groq Llama 3.3 70B
- **Vector Database**: Pinecone
- **Embeddings**: HuggingFace Sentence Transformers
- **Web Search**: DuckDuckGo
- **Frontend**: Streamlit
- **Framework**: LangChain

### Agent Communication
- Message passing between agents
- Shared context and collaboration
- Confidence scoring for responses
- Source attribution and citations

## 🌟 Key Benefits

1. **Specialized Expertise** - Each agent is optimized for specific domains
2. **Intelligent Collaboration** - Agents work together for comprehensive answers
3. **Cultural Sensitivity** - Respectful and accurate cultural information
4. **Practical Guidance** - Actionable recommendations with context
5. **Scalable Architecture** - Easy to add new specialized agents

## 🤝 Contributing

To add a new agent:
1. Create a new agent class inheriting from `BaseAgent`
2. Implement `_get_keywords()` and `_get_system_prompt()` methods
3. Add agent keywords to `AgentCoordinator.agent_keywords`
4. Update the UI to include the new agent

## 📄 License

This project is part of an academic research project for Information Retrieval and Web Analytics (IRWA).