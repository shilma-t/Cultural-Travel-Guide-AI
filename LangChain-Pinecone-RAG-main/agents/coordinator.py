"""
Agent Coordinator - Orchestrates multi-agent collaboration and query routing
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from .base_agent import BaseAgent
from .culture_agent import CultureAgent
from .activity_agent import ActivityAgent
from .food_agent import FoodAgent
from .language_agent import LanguageAgent


class AgentCoordinator:
    """Coordinates multiple specialized agents for comprehensive travel assistance"""
    
    def __init__(self, **kwargs):
        self.agents = {
            "culture": CultureAgent(**kwargs),
            "activity": ActivityAgent(**kwargs),
            "food": FoodAgent(**kwargs),
            "language": LanguageAgent(**kwargs)
        }
        
        # Keywords for determining which agents to involve
        self.agent_keywords = {
            "culture": [
                "culture", "cultural", "tradition", "customs", "etiquette", "festival",
                "ceremony", "heritage", "wedding", "ritual", "local", "regional"
            ],
            "activity": [
                "activities", "attractions", "things to do", "sightseeing", "tour",
                "visit", "explore", "museums", "temples", "parks", "hiking", "adventure"
            ],
            "food": [
                "food", "cuisine", "restaurant", "dining", "eat", "dish", "street food",
                "vegetarian", "vegan", "halal", "kosher", "allergies", "menu"
            ],
            "language": [
                "language", "translate", "phrases", "speak", "communication", "pronunciation",
                "greetings", "directions", "help", "emergency", "polite"
            ]
        }
    
    def analyze_query(self, query: str) -> Dict[str, float]:
        """Analyze query to determine which agents should be involved"""
        query_lower = query.lower()
        agent_scores = {}
        
        # Enhanced keyword matching with weights
        keyword_weights = {
            "culture": {
                "culture": 2, "cultural": 2, "tradition": 2, "customs": 2, "etiquette": 2,
                "festival": 2, "ceremony": 2, "heritage": 2, "wedding": 1, "ritual": 1,
                "local": 1, "regional": 1, "taboo": 1, "sacred": 1, "religious": 1
            },
            "activity": {
                "activities": 2, "attractions": 2, "things to do": 2, "sightseeing": 2,
                "tour": 2, "visit": 2, "explore": 2, "museums": 2, "temples": 2,
                "parks": 2, "hiking": 2, "adventure": 2, "itinerary": 3, "plan": 2,
                "schedule": 2, "day": 1, "morning": 1, "afternoon": 1, "evening": 1
            },
            "food": {
                "food": 2, "cuisine": 2, "restaurant": 2, "dining": 2, "eat": 2,
                "dish": 2, "street food": 2, "vegetarian": 1, "vegan": 1, "halal": 1,
                "kosher": 1, "allergies": 1, "menu": 1, "breakfast": 1, "lunch": 1,
                "dinner": 1, "snacks": 1, "drinks": 1
            },
            "language": {
                "language": 2, "translate": 2, "phrases": 2, "speak": 2, "communication": 2,
                "pronunciation": 2, "greetings": 2, "directions": 2, "help": 2,
                "emergency": 2, "polite": 1, "formal": 1, "informal": 1
            }
        }
        
        for agent_name, keywords in keyword_weights.items():
            score = 0
            for keyword, weight in keywords.items():
                if keyword in query_lower:
                    score += weight
            agent_scores[agent_name] = score
        
        return agent_scores
    
    def select_agents(self, query: str, threshold: float = 0.3) -> List[str]:
        """Select agents based on query analysis with enhanced itinerary detection"""
        scores = self.analyze_query(query)
        max_score = max(scores.values()) if scores.values() else 0
        
        # Special handling for itinerary/planning queries - ALWAYS use all agents
        if self._is_itinerary_query(query):
            print(f"🎯 Detected itinerary query: '{query}' - Using all agents for comprehensive planning")
            return ["culture", "activity", "food", "language"]  # All agents for comprehensive planning
        
        # Enhanced detection for travel-related queries
        query_lower = query.lower()
        travel_indicators = [
            "vietnam", "ho chi minh", "hanoi", "hoi an", "saigon",
            "visit", "travel", "trip", "vacation", "holiday", "destination"
        ]
        
        if any(indicator in query_lower for indicator in travel_indicators):
            print(f"🌍 Detected travel query: '{query}' - Using all agents for comprehensive guidance")
            return ["culture", "activity", "food", "language"]
        
        if max_score == 0:
            # If no specific keywords found, try to infer from context
            return self._infer_agents_from_context(query)
        
        selected_agents = []
        for agent_name, score in scores.items():
            if score > 0 and score / max_score >= threshold:
                selected_agents.append(agent_name)
        
        return selected_agents if selected_agents else ["culture"]  # Default fallback
    
    def _is_itinerary_query(self, query: str) -> bool:
        """Detect if query is asking for itinerary/planning"""
        itinerary_keywords = [
            "itinerary", "plan", "planning", "schedule", "day", "trip", "visit",
            "spend a day", "what to do", "things to do", "recommendations",
            "guide", "tour", "explore", "experience", "activities", "attractions",
            "plan a day", "day in", "visit", "travel to", "going to", "trip to",
            "vacation", "holiday", "sightseeing", "must see", "top places",
            "best places", "where to go", "what to see", "places to visit"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in itinerary_keywords)
    
    def _infer_agents_from_context(self, query: str) -> List[str]:
        """Infer which agents to use when no specific keywords are found"""
        query_lower = query.lower()
        
        # Common travel query patterns
        if any(word in query_lower for word in ["visit", "travel", "trip", "destination"]):
            return ["culture", "activity"]  # General travel queries
        elif any(word in query_lower for word in ["recommend", "suggest", "best"]):
            return ["culture", "activity", "food"]  # Recommendation queries
        elif any(word in query_lower for word in ["plan", "itinerary", "schedule"]):
            return ["culture", "activity", "food", "language"]  # Planning queries
        else:
            return ["culture"]  # Default to culture agent
    
    def coordinate_response(self, query: str) -> Dict[str, Any]:
        """Coordinate multiple agents to provide comprehensive response"""
        
        # Select relevant agents
        selected_agents = self.select_agents(query)
        
        if len(selected_agents) == 1:
            # Single agent response
            agent = self.agents[selected_agents[0]]
            result = agent.process_query(query)
            return {
                "response": result["response"],
                "sources": result["sources"],
                "agents_used": [result["agent"]],
                "collaboration": False
            }
        
        # Multi-agent collaboration with enhanced coordination
        agent_responses = []
        collaboration_context = ""
        
        # Get responses from all selected agents with iterative collaboration
        for i, agent_name in enumerate(selected_agents):
            agent = self.agents[agent_name]
            
            # Enhanced collaboration context for later agents
            enhanced_context = collaboration_context
            if i > 0:  # For agents after the first one
                enhanced_context += f"\n\nPrevious agent insights:\n"
                for j, prev_response in enumerate(agent_responses):
                    if prev_response["confidence"] > 0.5:
                        enhanced_context += f"- {prev_response['agent']}: {prev_response['response'][:150]}...\n"
            
            try:
                response = agent.process_query(query, enhanced_context)
                agent_responses.append(response)
                
                # Build collaboration context for next agents
                if response["confidence"] > 0.5:
                    collaboration_context += f"\n{agent_name.title()} Agent: {response['response'][:200]}...\n"
            except Exception as e:
                print(f"Error processing query with {agent_name} agent: {e}")
                # Add a fallback response for this agent
                fallback_response = {
                    "agent": agent_name,
                    "response": f"I encountered an issue processing your request. Please try rephrasing your question or ask for more specific information about {agent_name.lower()}.",
                    "sources": [],
                    "confidence": 0.1
                }
                agent_responses.append(fallback_response)
        
        # Enhanced response combination for itinerary queries
        if self._is_itinerary_query(query):
            combined_response = self._create_itinerary_response(agent_responses, query)
        else:
            combined_response = self._combine_responses(agent_responses, query)
        
        # Collect all sources
        all_sources = []
        for response in agent_responses:
            all_sources.extend(response.get("sources", []))
        
        return {
            "response": combined_response,
            "sources": list(set(all_sources)),  # Remove duplicates
            "agents_used": [resp["agent"] for resp in agent_responses],
            "collaboration": True,
            "individual_responses": agent_responses
        }
    
    def _combine_responses(self, responses: List[Dict[str, Any]], original_query: str) -> str:
        """Combine multiple agent responses into a coherent answer"""
        
        # Filter out low-confidence responses
        valid_responses = [r for r in responses if r["confidence"] > 0.3]
        
        if not valid_responses:
            return "I'm sorry, I couldn't find relevant information for your query."
        
        if len(valid_responses) == 1:
            return valid_responses[0]["response"]
        
        # Combine multiple responses
        combined_parts = []
        
        for i, response in enumerate(valid_responses, 1):
            agent_name = response["agent"]
            agent_response = response["response"]
            
            # Add section header
            combined_parts.append(f"**{agent_name.title()} Expert:**")
            combined_parts.append(agent_response)
            
            if i < len(valid_responses):
                combined_parts.append("")  # Add spacing between sections
        
        # Add collaboration note
        combined_parts.append(f"\n*This response combines insights from {len(valid_responses)} specialized agents to provide comprehensive travel guidance.*")
        
        return "\n".join(combined_parts)
    
    def _create_itinerary_response(self, responses: List[Dict[str, Any]], original_query: str) -> str:
        """Create a structured itinerary response combining all agent insights"""
        
        # Filter out low-confidence responses, but be more lenient for itinerary queries
        valid_responses = [r for r in responses if r["confidence"] > 0.1]
        
        if not valid_responses:
            return """I'm sorry, I couldn't find specific information for your itinerary request in my knowledge base. 

However, I can still help you plan your day! Here's what I recommend:

**🏛️ Cultural Insights**
- Research local customs and etiquette before your visit
- Check for any cultural events or festivals happening
- Learn about appropriate dress codes and behavior

**🎯 Activities & Attractions**
- Visit major landmarks and tourist attractions
- Explore local neighborhoods and markets
- Consider guided tours for better cultural understanding

**🍽️ Food & Dining**
- Try local specialties and traditional dishes
- Ask locals for restaurant recommendations
- Be adventurous with street food (safely)

**🗣️ Language & Communication**
- Learn basic greetings and polite phrases
- Download a translation app
- Carry a phrasebook for emergencies

Would you like me to provide more specific guidance for any particular aspect of your trip?"""
        
        # Organize responses by agent type
        agent_responses = {}
        for response in valid_responses:
            agent_name = response["agent"].lower()
            agent_responses[agent_name] = response["response"]
        
        # Create structured itinerary with enhanced formatting
        itinerary_parts = []
        itinerary_parts.append("## 🌍 Comprehensive Travel Itinerary")
        itinerary_parts.append("")
        
        # Extract destination from original query for context
        destination = self._extract_destination_from_query(original_query)
        if destination:
            itinerary_parts.append(f"**Destination:** {destination}")
            itinerary_parts.append("")
        
        # Cultural insights first
        if "culture" in agent_responses:
            itinerary_parts.append("### 🏛️ Cultural Insights")
            itinerary_parts.append(agent_responses["culture"])
            itinerary_parts.append("")
        
        # Activities and attractions
        if "activity" in agent_responses:
            itinerary_parts.append("### 🎯 Activities & Attractions")
            itinerary_parts.append(agent_responses["activity"])
            itinerary_parts.append("")
        
        # Food and dining
        if "food" in agent_responses:
            itinerary_parts.append("### 🍽️ Food & Dining")
            itinerary_parts.append(agent_responses["food"])
            itinerary_parts.append("")
        
        # Language and communication
        if "language" in agent_responses:
            itinerary_parts.append("### 🗣️ Language & Communication")
            itinerary_parts.append(agent_responses["language"])
            itinerary_parts.append("")
        
        # Add practical tips section
        itinerary_parts.append("### 💡 Practical Travel Tips")
        itinerary_parts.append("- Book tickets in advance for popular attractions")
        itinerary_parts.append("- Check opening hours and seasonal availability")
        itinerary_parts.append("- Download offline maps and translation apps")
        itinerary_parts.append("- Carry local currency and have backup payment methods")
        itinerary_parts.append("- Respect local customs and dress codes")
        itinerary_parts.append("")
        
        # Add collaboration note
        itinerary_parts.append("---")
        itinerary_parts.append(f"*This comprehensive itinerary was created by collaborating {len(valid_responses)} specialized AI agents to provide you with complete travel guidance.*")
        
        return "\n".join(itinerary_parts)
    
    def _extract_destination_from_query(self, query: str) -> str:
        """Extract destination from query for better context"""
        import re
        
        # Common destination patterns
        patterns = [
            r"in\s+([A-Z][A-Za-z\-\s]+)$",
            r"to\s+([A-Z][A-Za-z\-\s]+)$", 
            r"at\s+([A-Z][A-Za-z\-\s]+)$",
            r"(?:visit|travel to|going to|trip to)\s+([A-Z][A-Za-z\-\s]+)",
            r"day in\s+([A-Z][A-Za-z\-\s]+)",
            r"plan a day in\s+([A-Z][A-Za-z\-\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of each agent"""
        return {
            "culture": [
                "Cultural traditions and customs",
                "Social etiquette and manners", 
                "Religious and spiritual practices",
                "Festivals and celebrations",
                "Wedding traditions",
                "Social norms and taboos"
            ],
            "activity": [
                "Tourist attractions and landmarks",
                "Museums and cultural sites",
                "Outdoor activities and adventures",
                "Guided tours and excursions",
                "Entertainment and shows",
                "Nature and wildlife experiences"
            ],
            "food": [
                "Local and traditional cuisines",
                "Restaurant recommendations",
                "Street food and local specialties",
                "Dietary restrictions and preferences",
                "Food allergies and safety",
                "Food culture and traditions"
            ],
            "language": [
                "Common phrases and essential vocabulary",
                "Translation assistance",
                "Pronunciation guidance",
                "Cultural communication tips",
                "Language etiquette and manners",
                "Emergency and practical phrases"
            ]
        }
    
    def suggest_follow_up_questions(self, query: str, agents_used: List[str]) -> List[str]:
        """Suggest follow-up questions based on the query and agents used"""
        
        suggestions = []
        
        if "culture" in agents_used:
            suggestions.extend([
                "What cultural etiquette should I be aware of?",
                "Are there any cultural taboos I should avoid?",
                "What festivals or events happen during my visit?"
            ])
        
        if "activity" in agents_used:
            suggestions.extend([
                "What are some budget-friendly activities?",
                "Are there any family-friendly attractions?",
                "What outdoor activities are available?"
            ])
        
        if "food" in agents_used:
            suggestions.extend([
                "What are the must-try local dishes?",
                "Are there vegetarian-friendly restaurants?",
                "What street food should I try?"
            ])
        
        if "language" in agents_used:
            suggestions.extend([
                "What are some essential phrases I should learn?",
                "How do I ask for directions?",
                "What are some polite greetings?"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
