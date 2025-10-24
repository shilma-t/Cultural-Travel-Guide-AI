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
        
        for agent_name, keywords in self.agent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            agent_scores[agent_name] = score
        
        return agent_scores
    
    def select_agents(self, query: str, threshold: float = 0.3) -> List[str]:
        """Select agents based on query analysis"""
        scores = self.analyze_query(query)
        max_score = max(scores.values()) if scores.values() else 0
        
        if max_score == 0:
            # If no specific keywords found, try to infer from context
            return self._infer_agents_from_context(query)
        
        selected_agents = []
        for agent_name, score in scores.items():
            if score > 0 and score / max_score >= threshold:
                selected_agents.append(agent_name)
        
        return selected_agents if selected_agents else ["culture"]  # Default fallback
    
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
        
        # Multi-agent collaboration
        agent_responses = []
        collaboration_context = ""
        
        # Get responses from all selected agents
        for agent_name in selected_agents:
            agent = self.agents[agent_name]
            response = agent.process_query(query, collaboration_context)
            agent_responses.append(response)
            
            # Build collaboration context
            if response["confidence"] > 0.5:
                collaboration_context += f"\n{agent_name.title()} Agent: {response['response'][:200]}...\n"
        
        # Combine responses
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
