# Enhanced ingestion.py with comprehensive travel data

import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# LangChain imports
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

# -------------------- Pinecone Setup --------------------
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = os.environ.get("PINECONE_INDEX_NAME")

existing_indexes = [idx["name"] for idx in pc.list_indexes()]
if index_name not in existing_indexes:
    print(f"Creating Pinecone index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    # Wait until ready
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)

# -------------------- Embeddings --------------------
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# -------------------- Create Comprehensive Travel Data --------------------
def create_travel_documents():
    """Create comprehensive travel documents for major cities"""
    cities_data = {
        "Tokyo": {
            "country": "Japan",
            "culture": "Bow when greeting, remove shoes indoors, be punctual, respect for elders, group harmony, Cherry Blossom Festival (March-April)",
            "activities": "Morning: Senso-ji Temple (Asakusa), Tsukiji Outer Market, Meiji Shrine. Afternoon: Tokyo National Museum, Shibuya Crossing, Harajuku District. Evening: Tokyo Skytree, Shibuya Sky, Traditional Izakaya in Golden Gai",
            "food": "Breakfast: Tsukiji Outer Market sushi, Traditional Japanese breakfast. Lunch: Ramen at Ichiran, Sushi at Tsukiji, Tempura at Tenkuni. Dinner: Kaiseki at Kikunoi, Yakitori at Torikizoku, Sukiyaki at Imahan",
            "language": "Essential: Konnichiwa (Hello), Arigato (Thank you), Sumimasen (Excuse me). Dining: Oishii (Delicious), Okanjo onegaishimasu (Check please). Directions: Doko desu ka? (Where is it?), Migi (Right), Hidari (Left)"
        },
        "Paris": {
            "country": "France", 
            "culture": "Greet with Bonjour, kiss on cheeks, dress well, be polite, art appreciation, café culture, leisurely dining, Bastille Day (July 14)",
            "activities": "Morning: Louvre Museum, Notre-Dame Cathedral, Sainte-Chapelle. Afternoon: Eiffel Tower, Seine River Cruise, Montmartre District. Evening: Champs-Élysées, Arc de Triomphe, Traditional Bistro Dinner",
            "food": "Breakfast: Croissants at local boulangerie, Café au lait, Pain au chocolat. Lunch: Bistro lunch, Crêpes, Quiche Lorraine. Dinner: Traditional French cuisine, Wine tasting, Cheese platter",
            "language": "Essential: Bonjour (Hello), Merci (Thank you), Excusez-moi (Excuse me). Dining: L'addition s'il vous plaît (Check please), C'est délicieux (It's delicious). Directions: Où est...? (Where is...?), À droite (Right), À gauche (Left)"
        },
        "Rome": {
            "country": "Italy",
            "culture": "Greet with Ciao, dress modestly for churches, be expressive, family values, food culture, religious traditions, Easter celebrations",
            "activities": "Morning: Colosseum, Roman Forum, Palatine Hill. Afternoon: Vatican Museums, Sistine Chapel, St. Peter's Basilica. Evening: Trevi Fountain, Spanish Steps, Trastevere District",
            "food": "Breakfast: Cappuccino and cornetto, Espresso at local bar. Lunch: Traditional Roman pasta, Pizza al taglio, Gelato. Dinner: Cacio e Pepe, Saltimbocca, Tiramisu",
            "language": "Essential: Ciao (Hello), Grazie (Thank you), Scusi (Excuse me). Dining: Il conto per favore (Check please), È buonissimo (It's very good). Directions: Dove si trova...? (Where is...?), A destra (Right), A sinistra (Left)"
        },
        "Bangkok": {
            "country": "Thailand",
            "culture": "Wai greeting, remove shoes, dress modestly, respect for monarchy, Buddhist traditions, respect for elders, Songkran (April)",
            "activities": "Morning: Grand Palace, Wat Pho Temple, Wat Arun. Afternoon: Chatuchak Weekend Market, Jim Thompson House, Boat tour on Chao Phraya. Evening: Khao San Road, Rooftop bars, Traditional Thai massage",
            "food": "Breakfast: Jok (Rice porridge), Khao tom (Rice soup), Thai coffee. Lunch: Pad Thai, Som Tam (Papaya salad), Tom Yum soup. Dinner: Street food at Chinatown, Traditional Thai restaurant, Mango sticky rice",
            "language": "Essential: Sawasdee (Hello), Khop khun (Thank you), Khor thot (Excuse me). Dining: Check bin (Check please), Aroi (Delicious). Directions: Yu tee nai? (Where is it?), Kwa (Right), Sai (Left)"
        },
        "New York": {
            "country": "United States",
            "culture": "Direct communication, be punctual, tip 15-20%, respect personal space, diversity celebration, fast-paced lifestyle, New Year's Eve in Times Square",
            "activities": "Morning: Central Park, Statue of Liberty, 9/11 Memorial. Afternoon: Metropolitan Museum, High Line Park, Brooklyn Bridge. Evening: Times Square, Broadway Show, Rooftop bars",
            "food": "Breakfast: Bagels and lox, Pancakes, Coffee from local deli. Lunch: NYC pizza slice, Hot dog from cart, Deli sandwich. Dinner: Steakhouse dinner, Ethnic cuisine, Dessert at local bakery",
            "language": "Essential: Hello, Thank you, Excuse me. Dining: Check please, This is delicious. Directions: Where is...?, Right, Left"
        },
        "Ho Chi Minh City": {
            "country": "Vietnam",
            "culture": "Respect for elders, remove shoes indoors, bow slightly when greeting, avoid pointing with finger, use both hands when giving/receiving, Tet Festival (January-February), respect for ancestors, Buddhist traditions",
            "activities": "Morning: War Remnants Museum, Independence Palace, Notre-Dame Cathedral. Afternoon: Ben Thanh Market, Saigon Central Post Office, Jade Emperor Pagoda. Evening: Bitexco Financial Tower Skydeck, Nguyen Hue Walking Street, Traditional Water Puppet Show",
            "food": "Breakfast: Pho bo (beef noodle soup), Banh mi (Vietnamese sandwich), Ca phe sua da (Vietnamese iced coffee). Lunch: Bun cha (grilled pork with noodles), Goi cuon (fresh spring rolls), Banh xeo (Vietnamese pancake). Dinner: Com tam (broken rice), Cha ca (grilled fish), Che (Vietnamese dessert)",
            "language": "Essential: Xin chao (Hello), Cam on (Thank you), Xin loi (Excuse me). Dining: Tinh tien (Check please), Ngon qua (It's delicious). Directions: O dau? (Where is it?), Ben phai (Right), Ben trai (Left)"
        },
        "Hanoi": {
            "country": "Vietnam", 
            "culture": "Traditional Vietnamese values, respect for family and ancestors, Buddhist and Confucian influences, Tet celebrations, water puppet shows, traditional music, respect for teachers and elders",
            "activities": "Morning: Ho Chi Minh Mausoleum, One Pillar Pagoda, Temple of Literature. Afternoon: Old Quarter walking tour, Hoan Kiem Lake, Thang Long Imperial Citadel. Evening: Water Puppet Show, Dong Xuan Market, Street food tour in Old Quarter",
            "food": "Breakfast: Pho ga (chicken noodle soup), Banh cuon (steamed rice rolls), Ca phe trung (egg coffee). Lunch: Bun bo Hue (spicy beef noodle soup), Banh mi Hanoi, Nem ran (fried spring rolls). Dinner: Cha ca La Vong (grilled fish), Bun cha, Che troi nuoc (sweet soup)",
            "language": "Essential: Xin chao (Hello), Cam on (Thank you), Xin loi (Excuse me). Dining: Tinh tien (Check please), Ngon qua (It's delicious). Directions: O dau? (Where is it?), Ben phai (Right), Ben trai (Left)"
        },
        "Hoi An": {
            "country": "Vietnam",
            "culture": "Ancient town preservation, lantern festivals, traditional crafts, respect for heritage architecture, monthly lantern festival, traditional Vietnamese customs, family values, ancestor worship",
            "activities": "Morning: Hoi An Ancient Town walking tour, Japanese Covered Bridge, Assembly Hall of the Fujian Chinese Congregation. Afternoon: Tailor shops, Traditional handicraft workshops, Thanh Ha Pottery Village. Evening: Lantern boat ride, Night market, Traditional music performance",
            "food": "Breakfast: Cao lau (local noodle dish), Banh mi Hoi An, Fresh fruit smoothies. Lunch: White rose dumplings, Banh xeo (Vietnamese pancake), Com ga (chicken rice). Dinner: Seafood at Cua Dai Beach, Banh bao banh vac (white rose dumplings), Che (Vietnamese dessert)",
            "language": "Essential: Xin chao (Hello), Cam on (Thank you), Xin loi (Excuse me). Dining: Tinh tien (Check please), Ngon qua (It's delicious). Directions: O dau? (Where is it?), Ben phai (Right), Ben trai (Left)"
        }
    }
    
    documents = []
    for city, data in cities_data.items():
        # Create comprehensive document for each city
        content = f"""
        Complete Travel Guide for {city}, {data['country']}
        
        Cultural Insights:
        {data['culture']}
        
        Activities and Attractions:
        {data['activities']}
        
        Food and Dining:
        {data['food']}
        
        Language and Communication:
        {data['language']}
        
        Travel Tips:
        - Book tickets in advance for popular attractions
        - Check opening hours and seasonal availability
        - Try local specialties and traditional dishes
        - Learn basic greetings in the local language
        - Respect local customs and traditions
        """
        
        documents.append(Document(
            page_content=content,
            metadata={
                "source": f"travel_guide_{city.lower()}.txt",
                "city": city,
                "country": data['country'],
                "type": "comprehensive_guide"
            }
        ))
    
    return documents

# -------------------- Load PDFs --------------------
documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
pdf_files = [f for f in os.listdir(documents_dir) if f.endswith(".pdf")]

raw_documents = []
if pdf_files:
    for pdf_file in pdf_files:
        pdf_path = os.path.join(documents_dir, pdf_file)
        print(f"Loading {pdf_file}...")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        for d in docs:
            d.metadata["source"] = pdf_file
            d.metadata["type"] = "pdf_document"
        raw_documents.extend(docs)
    print(f"✅ Loaded {len(raw_documents)} pages from {len(pdf_files)} PDF files")
else:
    print("No PDF files found, using travel data only")

# -------------------- Create Travel Documents --------------------
print("🌍 Creating comprehensive travel data...")
travel_documents = create_travel_documents()
print(f"✅ Created {len(travel_documents)} travel guide documents")

# Combine all documents
all_documents = raw_documents + travel_documents

# -------------------- Split Documents --------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
documents = text_splitter.split_documents(all_documents)
print(f"✅ Split into {len(documents)} chunks")

# -------------------- Add to Pinecone --------------------
print("📤 Adding documents to Pinecone...")
uuids = [f"enhanced_id_{i}" for i in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)
print(f"✅ Added {len(documents)} chunks to Pinecone index '{index_name}'")
print("🎉 Enhanced knowledge base with comprehensive travel data is ready!")
print("🌍 Cities included: Tokyo, Paris, Rome, Bangkok, New York")
print("📚 Categories: Culture, Activities, Food, Language")
print("🚀 Your multi-agent system is now ready for detailed itinerary queries!")
