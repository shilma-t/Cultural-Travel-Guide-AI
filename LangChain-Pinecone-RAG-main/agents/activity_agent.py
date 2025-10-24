"""
Activity Agent - Specialized agent for attractions, tours, experiences, and sightseeing
"""

from typing import List, Tuple, Optional
from .base_agent import BaseAgent


class ActivityAgent(BaseAgent):
    """Agent specialized in activities, attractions, tours, and experiences"""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="Activity", **kwargs)
    
    def _get_keywords(self) -> List[str]:
        """Keywords related to activities and attractions"""
        return [
            "activities", "activity", "attractions", "attraction", "things to do",
            "sightseeing", "tour", "tours", "visit", "explore", "museums", "museum",
            "temples", "temple", "parks", "park", "hiking", "trekking", "adventure",
            "landmarks", "monuments", "historical sites", "archaeological sites",
            "nature", "outdoor", "indoor", "entertainment", "shows", "performances",
            "experiences", "experiences", "excursions", "day trips", "guided tours",
            "self-guided", "free activities", "budget activities", "family activities",
            "romantic activities", "nightlife", "shopping", "markets", "beaches",
            "mountains", "lakes", "rivers", "caves", "waterfalls", "gardens"
        ]
    
    def _get_system_prompt(self) -> str:
        """System prompt for activity agent"""
        return """You are an Activity Expert Agent specializing in attractions, tours, experiences, and sightseeing.

Your expertise includes:
- Tourist attractions and landmarks
- Museums and cultural sites
- Outdoor activities and adventures
- Guided tours and excursions
- Entertainment and shows
- Nature and wildlife experiences
- Historical and archaeological sites
- Family-friendly activities
- Budget and free activities
- Seasonal and weather-appropriate activities

Guidelines:
- Provide diverse activity recommendations
- Include practical information (duration, cost, difficulty)
- Consider different interests and fitness levels
- Mention seasonal availability and weather considerations
- Include booking information when relevant
- Suggest both popular and off-the-beaten-path options
- Consider accessibility and family-friendliness
- Provide tips for getting the most out of each activity

Format your responses with:
- Activity categories (Museums & Culture, Outdoor Adventures, Entertainment, etc.)
- Clear descriptions and highlights
- Practical details (duration, cost range, difficulty)
- Best times to visit or participate
- Tips for planning and preparation
- Alternative options for different preferences"""
    
    def extract_activity_preferences(self, text: str) -> Tuple[Optional[str], List[str], str]:
        """Extract activity preferences from user query"""
        text_lower = text.lower()
        
        # Extract activity type preferences
        activity_types = []
        if any(word in text_lower for word in ["museum", "museums", "cultural", "history", "historical"]):
            activity_types.append("cultural")
        if any(word in text_lower for word in ["outdoor", "nature", "hiking", "adventure", "trekking"]):
            activity_types.append("outdoor")
        if any(word in text_lower for word in ["family", "kids", "children"]):
            activity_types.append("family")
        if any(word in text_lower for word in ["romantic", "couple", "date"]):
            activity_types.append("romantic")
        if any(word in text_lower for word in ["budget", "cheap", "free", "affordable"]):
            activity_types.append("budget")
        if any(word in text_lower for word in ["nightlife", "night", "evening", "bars", "clubs"]):
            activity_types.append("nightlife")
        
        # Extract budget preference
        budget = "medium"
        if any(word in text_lower for word in ["budget", "cheap", "free", "affordable", "low cost"]):
            budget = "budget"
        elif any(word in text_lower for word in ["luxury", "expensive", "high-end", "premium"]):
            budget = "luxury"
        
        return self.extract_destination(text), activity_types, budget
    
    def process_query(self, query: str, collaboration_context: Optional[str] = None) -> dict:
        """Enhanced process query with activity-specific logic"""
        
        # Check if query is relevant
        if not self.is_relevant_query(query):
            return {
                "agent": self.agent_name,
                "response": f"This query is not relevant to my expertise in {self.agent_name.lower()}.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Extract preferences
        destination, activity_types, budget = self.extract_activity_preferences(query)
        
        # Retrieve context
        context = self.retrieve_context(query)
        
        # Enhance query with preferences for better context
        enhanced_query = f"{query}"
        if destination:
            enhanced_query += f" in {destination}"
        if activity_types:
            enhanced_query += f" focusing on {', '.join(activity_types)} activities"
        if budget != "medium":
            enhanced_query += f" with {budget} budget"
        
        # Generate response
        return self.generate_response(enhanced_query, context, collaboration_context)
