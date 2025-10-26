"""
Language Agent - Specialized agent for language help, translations, and communication tips
"""

from typing import List, Dict, Optional
from .base_agent import BaseAgent


class LanguageAgent(BaseAgent):
    """Agent specialized in language help, translations, and communication tips"""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="Language", **kwargs)
    
    def _get_keywords(self) -> List[str]:
        """Keywords related to language and communication"""
        return [
            "language", "languages", "translate", "translation", "speak", "speaking",
            "communication", "communicate", "phrase", "phrases", "words", "vocabulary",
            "pronunciation", "pronounce", "accent", "dialect", "local language",
            "native language", "official language", "common phrases", "useful phrases",
            "greetings", "hello", "thank you", "please", "excuse me", "sorry",
            "directions", "asking for help", "emergency", "numbers", "time", "date",
            "shopping", "restaurant", "hotel", "transportation", "travel phrases",
            "polite", "formal", "informal", "conversation", "basic", "essential",
            "language barrier", "communication tips", "gestures", "body language",
            "cultural communication", "etiquette", "manners", "respectful"
        ]
    
    def _get_system_prompt(self) -> str:
        """System prompt for language agent"""
        return """You are a Language Expert Agent specializing in communication, translations, and language assistance.

Your expertise includes:
- Common phrases and essential vocabulary
- Translation assistance
- Pronunciation guidance
- Cultural communication tips
- Language etiquette and manners
- Emergency and practical phrases
- Regional language variations
- Communication strategies for travelers
- Non-verbal communication tips
- Language learning resources

Guidelines:
- Provide practical, commonly used phrases
- Include pronunciation guides when helpful
- Explain cultural context for language use
- Mention formal vs informal language usage
- Include emergency and safety-related phrases
- Provide tips for overcoming language barriers
- Suggest alternative communication methods
- Include cultural communication etiquette
- Mention regional variations and dialects
- Provide confidence-building tips for language learners

For itinerary planning:
- Provide phrases for common travel situations
- Include language tips for specific activities and dining
- Suggest communication strategies for cultural sites
- Provide phrases for asking directions and recommendations
- Include language etiquette for different cultural contexts
- Recommend language learning resources for the destination
- Provide emergency phrases and safety communication
- Include tips for non-verbal communication and gestures

Format your responses with:
- Essential phrases with translations
- Pronunciation tips (phonetic or simple guides)
- Cultural context and usage notes
- Formal vs informal variations
- Emergency and practical phrases
- Communication tips and strategies
- Cultural etiquette considerations
- Alternative communication methods
- For itineraries: situation-specific language guidance"""
    
    def extract_language_preferences(self, text: str) -> Dict[str, str]:
        """Extract language preferences from user query"""
        text_lower = text.lower()
        
        # Extract target language
        target_language = "local"
        common_languages = [
            "english", "spanish", "french", "german", "italian", "portuguese",
            "chinese", "japanese", "korean", "arabic", "hindi", "russian",
            "thai", "vietnamese", "indonesian", "malay", "tagalog", "dutch",
            "swedish", "norwegian", "danish", "finnish", "polish", "czech"
        ]
        
        for lang in common_languages:
            if lang in text_lower:
                target_language = lang
                break
        
        # Extract context/situation
        context = "general"
        if any(word in text_lower for word in ["emergency", "help", "urgent"]):
            context = "emergency"
        elif any(word in text_lower for word in ["restaurant", "food", "dining"]):
            context = "dining"
        elif any(word in text_lower for word in ["shopping", "buy", "purchase"]):
            context = "shopping"
        elif any(word in text_lower for word in ["directions", "where", "how to get"]):
            context = "directions"
        elif any(word in text_lower for word in ["hotel", "accommodation"]):
            context = "accommodation"
        elif any(word in text_lower for word in ["transport", "taxi", "bus", "train"]):
            context = "transportation"
        
        # Extract formality level
        formality = "neutral"
        if any(word in text_lower for word in ["formal", "polite", "respectful"]):
            formality = "formal"
        elif any(word in text_lower for word in ["casual", "informal", "friendly"]):
            formality = "informal"
        
        return {
            "target_language": target_language,
            "context": context,
            "formality": formality
        }
    
    def get_essential_phrases(self, context: str, formality: str) -> Dict[str, List[str]]:
        """Get essential phrases based on context and formality"""
        
        phrases = {
            "greetings": {
                "formal": ["Good morning", "Good afternoon", "Good evening", "How do you do?"],
                "informal": ["Hello", "Hi", "Hey", "Good day"],
                "neutral": ["Hello", "Good morning", "Good afternoon", "Good evening"]
            },
            "polite": {
                "formal": ["Please", "Thank you very much", "Excuse me", "I apologize"],
                "informal": ["Please", "Thanks", "Sorry", "Excuse me"],
                "neutral": ["Please", "Thank you", "Excuse me", "Sorry"]
            },
            "emergency": {
                "formal": ["Help!", "Emergency!", "Call the police", "I need a doctor"],
                "informal": ["Help!", "Emergency!", "Call police", "Need doctor"],
                "neutral": ["Help!", "Emergency!", "Call police", "Need doctor"]
            },
            "directions": {
                "formal": ["Excuse me, where is...?", "Could you please tell me how to get to...?"],
                "informal": ["Where is...?", "How do I get to...?"],
                "neutral": ["Where is...?", "How do I get to...?", "Excuse me, where is...?"]
            }
        }
        
        return phrases.get(context, phrases["greetings"])
    
    def process_query(self, query: str, collaboration_context: Optional[str] = None) -> dict:
        """Enhanced process query with language-specific logic"""
        
        # Check if query is relevant
        if not self.is_relevant_query(query):
            return {
                "agent": self.agent_name,
                "response": f"This query is not relevant to my expertise in {self.agent_name.lower()}.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Extract preferences
        preferences = self.extract_language_preferences(query)
        destination = self.extract_destination(query)
        
        # Retrieve context
        context = self.retrieve_context(query)
        
        # Enhance query with preferences for better context
        enhanced_query = f"{query}"
        if destination:
            enhanced_query += f" for {destination}"
        enhanced_query += f" (context: {preferences['context']}, formality: {preferences['formality']})"
        
        # Generate response
        return self.generate_response(enhanced_query, context, collaboration_context)
