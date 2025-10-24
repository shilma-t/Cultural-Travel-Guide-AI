"""
Food Agent - Specialized agent for cuisine, restaurants, dietary preferences, and food experiences
"""

import re
from typing import List, Tuple, Optional
from .base_agent import BaseAgent


class FoodAgent(BaseAgent):
    """Agent specialized in food, cuisine, restaurants, and dietary preferences"""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="Food", **kwargs)
    
    def _get_keywords(self) -> List[str]:
        """Keywords related to food and dining"""
        return [
            "food", "foods", "cuisine", "dish", "dishes", "eat", "eating", "dining",
            "restaurant", "restaurants", "cafe", "café", "bar", "bars", "street food",
            "local food", "traditional food", "breakfast", "lunch", "dinner", "brunch",
            "snacks", "desserts", "drinks", "beverages", "vegetarian", "vegan",
            "halal", "kosher", "gluten-free", "allergies", "dietary", "spicy",
            "mild", "sweet", "sour", "bitter", "flavors", "ingredients", "recipes",
            "cooking", "chef", "menu", "price", "budget", "expensive", "cheap",
            "fine dining", "casual dining", "fast food", "food market", "food tour"
        ]
    
    def _get_system_prompt(self) -> str:
        """System prompt for food agent"""
        return """You are a Food Expert Agent specializing in cuisine, restaurants, and dining experiences.

Your expertise includes:
- Local and traditional cuisines
- Restaurant recommendations
- Street food and local specialties
- Dietary restrictions and preferences
- Food allergies and safety
- Cooking methods and ingredients
- Food culture and traditions
- Budget-friendly dining options
- Fine dining experiences
- Food tours and experiences

Guidelines:
- Provide diverse food recommendations
- Always consider dietary restrictions and allergies
- Include price ranges and budget considerations
- Mention food safety and hygiene tips
- Explain cultural significance of dishes
- Provide practical dining tips
- Include both popular and hidden gem recommendations
- Consider different meal times and occasions
- Mention any cultural dining etiquette

Format your responses with:
- Food categories (Street Food, Traditional Cuisine, Fine Dining, etc.)
- Clear descriptions of dishes and flavors
- Price ranges and budget considerations
- Dietary restriction information
- Cultural context and significance
- Practical tips for ordering and dining
- Recommendations for different occasions"""
    
    def extract_dietary_preferences(self, text: str) -> Tuple[bool, bool, List[str]]:
        """Extract dietary preferences from user query"""
        text_lower = text.lower()
        
        # Check for vegetarian/vegan preferences
        is_vegetarian = False
        is_vegan = False
        
        if re.search(r"\b(vegetarian|veg-only|veg friendly|veg-friendly)\b", text_lower):
            is_vegetarian = True
        if re.search(r"\b(vegan|plant-based)\b", text_lower):
            is_vegan = True
        if re.search(r"\b(non-veg|non veg|meat lover|steak)\b", text_lower):
            is_vegetarian = False
            is_vegan = False
        
        # Extract allergies
        known_allergens = [
            "peanut", "peanuts", "tree nut", "tree nuts", "nut", "nuts", "almond", 
            "cashew", "walnut", "pistachio", "hazelnut", "pecan", "macadamia", 
            "brazil nut", "sesame", "soy", "soya", "gluten", "wheat", "dairy", 
            "milk", "lactose", "egg", "eggs", "shellfish", "shrimp", "prawn", 
            "crab", "lobster", "mollusk", "clam", "oyster", "fish", "mustard"
        ]
        
        allergies = []
        if "allerg" in text_lower or re.search(r"\bno\s+\w+\b", text_lower):
            for allergen in known_allergens:
                if re.search(rf"\b{re.escape(allergen)}\b", text_lower):
                    allergies.append(allergen)
        
        # Normalize unique singular terms
        normalized = []
        for a in allergies:
            a_s = a.rstrip('s')
            if a_s not in normalized:
                normalized.append(a_s)
        
        return is_vegetarian, is_vegan, normalized
    
    def extract_food_preferences(self, text: str) -> Tuple[Optional[str], str, List[str]]:
        """Extract food preferences including budget and meal type"""
        text_lower = text.lower()
        
        # Extract meal type
        meal_type = "any"
        if any(word in text_lower for word in ["breakfast", "morning"]):
            meal_type = "breakfast"
        elif any(word in text_lower for word in ["lunch", "midday"]):
            meal_type = "lunch"
        elif any(word in text_lower for word in ["dinner", "evening", "night"]):
            meal_type = "dinner"
        elif any(word in text_lower for word in ["brunch"]):
            meal_type = "brunch"
        
        # Extract budget preference
        budget = "medium"
        if any(word in text_lower for word in ["budget", "cheap", "affordable", "street food"]):
            budget = "budget"
        elif any(word in text_lower for word in ["luxury", "expensive", "fine dining", "high-end"]):
            budget = "luxury"
        
        # Extract dietary preferences
        is_veg, is_vegan, allergies = self.extract_dietary_preferences(text)
        
        return self.extract_destination(text), budget, allergies
    
    def process_query(self, query: str, collaboration_context: Optional[str] = None) -> dict:
        """Enhanced process query with food-specific logic"""
        
        # Check if query is relevant
        if not self.is_relevant_query(query):
            return {
                "agent": self.agent_name,
                "response": f"This query is not relevant to my expertise in {self.agent_name.lower()}.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Extract preferences
        destination, budget, allergies = self.extract_food_preferences(query)
        is_veg, is_vegan, _ = self.extract_dietary_preferences(query)
        
        # Retrieve context
        context = self.retrieve_context(query)
        
        # Enhance query with preferences for better context
        enhanced_query = f"{query}"
        if destination:
            enhanced_query += f" in {destination}"
        if budget != "medium":
            enhanced_query += f" with {budget} budget"
        if is_vegetarian:
            enhanced_query += " (vegetarian options)"
        if is_vegan:
            enhanced_query += " (vegan options)"
        if allergies:
            enhanced_query += f" (avoiding: {', '.join(allergies)})"
        
        # Generate response
        return self.generate_response(enhanced_query, context, collaboration_context)
