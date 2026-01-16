"""
AI utilities for natural language processing and service matching
Uses Google Gemini API for intent extraction and explanation generation
"""
import os
import json
import re
from typing import Dict, List, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY and GEMINI_AVAILABLE:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"Warning: Failed to configure Gemini: {e}")
        model = None
else:
    model = None

def extract_intent(query: str) -> Dict:
    """
    Extract service requirements from natural language query using LLM
    
    Args:
        query: Natural language query from user
        
    Returns:
        Dictionary with extracted intent:
        {
            'serviceType': str,
            'purpose': str,
            'crop': str,
            'acreage': int,
            'urgency': str,
            'budget': int,
            'specialRequirements': list
        }
    """
    if not model:
        # Fallback: basic keyword extraction
        return _extract_intent_fallback(query)
    
    try:
        prompt = f"""You are an AI assistant for RuralConnect, a rural services marketplace.

Extract service requirements from the customer's query and return structured JSON.

Query: "{query}"

Extract the following information:
1. Service type (tractor, jcb, auto, farm_service)
2. Purpose (plowing, harvesting, transportation, etc.)
3. Crop type (if mentioned: rice, wheat, cotton, etc.)
4. Acreage/land size (number of acres)
5. Urgency (immediate, this week, this month, flexible)
6. Budget range (price per hour or trip)
7. Special requirements (if any)

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "serviceType": "tractor" or "jcb" or "auto" or "farm_service" or "",
  "purpose": "plowing" or "harvesting" or "transportation" or "",
  "crop": "rice" or "wheat" or "cotton" or "",
  "acreage": number or null,
  "urgency": "immediate" or "this week" or "this month" or "flexible" or "",
  "budget": number or null,
  "specialRequirements": []
}}

If information is not mentioned, use empty string for strings, null for numbers."""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=500,
            )
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        # Parse JSON
        intent = json.loads(response_text)
        
        # Validate and normalize
        intent = _normalize_intent(intent)
        
        return intent
        
    except Exception as e:
        print(f"Error in LLM intent extraction: {e}")
        # Fallback to keyword extraction
        return _extract_intent_fallback(query)


def _extract_intent_fallback(query: str) -> Dict:
    """
    Fallback keyword-based intent extraction if LLM is unavailable
    """
    query_lower = query.lower()
    
    # Extract service type
    service_type = ""
    if 'tractor' in query_lower:
        service_type = "tractor"
    elif 'jcb' in query_lower:
        service_type = "jcb"
    elif 'auto' in query_lower:
        service_type = "auto"
    elif 'farm' in query_lower:
        service_type = "farm_service"
    
    # Extract purpose
    purpose = ""
    if 'plow' in query_lower or 'plough' in query_lower:
        purpose = "plowing"
    elif 'harvest' in query_lower:
        purpose = "harvesting"
    elif 'transport' in query_lower or 'carry' in query_lower:
        purpose = "transportation"
    
    # Extract crop
    crop = ""
    if 'rice' in query_lower:
        crop = "rice"
    elif 'wheat' in query_lower:
        crop = "wheat"
    elif 'cotton' in query_lower:
        crop = "cotton"
    
    # Extract acreage
    acreage = None
    acreage_match = re.search(r'(\d+)\s*(?:acre|acres|एकड़)', query_lower)
    if acreage_match:
        acreage = int(acreage_match.group(1))
    
    # Extract urgency
    urgency = ""
    if 'urgent' in query_lower or 'immediate' in query_lower or 'now' in query_lower:
        urgency = "immediate"
    elif 'week' in query_lower:
        urgency = "this week"
    elif 'month' in query_lower:
        urgency = "this month"
    else:
        urgency = "flexible"
    
    # Extract budget
    budget = None
    budget_match = re.search(r'(?:₹|rs|rupee|budget|price)[\s:]*(\d+)', query_lower)
    if budget_match:
        budget = int(budget_match.group(1))
    
    return {
        "serviceType": service_type,
        "purpose": purpose,
        "crop": crop,
        "acreage": acreage,
        "urgency": urgency,
        "budget": budget,
        "specialRequirements": []
    }


def _normalize_intent(intent: Dict) -> Dict:
    """
    Normalize extracted intent to ensure valid format
    """
    return {
        "serviceType": str(intent.get("serviceType", "")).lower().strip() or "",
        "purpose": str(intent.get("purpose", "")).lower().strip() or "",
        "crop": str(intent.get("crop", "")).lower().strip() or "",
        "acreage": int(intent.get("acreage", 0)) if intent.get("acreage") else None,
        "urgency": str(intent.get("urgency", "")).lower().strip() or "",
        "budget": int(intent.get("budget", 0)) if intent.get("budget") else None,
        "specialRequirements": intent.get("specialRequirements", []) or []
    }


def generate_explanation(service_data: Dict, customer_intent: Dict) -> str:
    """
    Generate AI explanation for why a service matches customer requirements
    
    Args:
        service_data: Service provider data
        customer_intent: Extracted customer intent
        
    Returns:
        Natural language explanation string
    """
    if not model:
        # Fallback: simple template-based explanation
        return _generate_explanation_fallback(service_data, customer_intent)
    
    try:
        prompt = f"""You are an AI assistant explaining service matches to customers in RuralConnect.

Service Provider: {service_data.get('providerName', 'Unknown')}
Service Type: {service_data.get('type', '')}
Location: {service_data.get('village', '')}, {service_data.get('district', '')}
Price: ₹{service_data.get('pricePerHour') or service_data.get('pricePerTrip', 0)} per {'hour' if service_data.get('pricePerHour') else 'trip'}
Distance: {service_data.get('distance', 0):.1f} km away

Customer Requirements:
- Service Type: {customer_intent.get('serviceType', 'any')}
- Purpose: {customer_intent.get('purpose', 'any')}
- Crop: {customer_intent.get('crop', 'any')}
- Budget: ₹{customer_intent.get('budget', 'flexible')}

Generate a brief (2-3 sentences) explanation of why this provider is a good match.
Focus on: location match, price fit, availability, and any unique advantages.
Be friendly, helpful, and conversational. Suitable for rural Indian customers.

Return ONLY the explanation text, no additional formatting."""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=200,
            )
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Error in LLM explanation generation: {e}")
        return _generate_explanation_fallback(service_data, customer_intent)


def _generate_explanation_fallback(service_data: Dict, customer_intent: Dict) -> str:
    """
    Fallback template-based explanation if LLM is unavailable
    """
    explanations = []
    
    # Location match
    distance = service_data.get('distance', 0)
    if distance < 1:
        explanations.append("Same village location ensures quick service.")
    elif distance < 5:
        explanations.append("Nearby location makes it convenient.")
    
    # Price match
    customer_budget = customer_intent.get('budget')
    service_price = service_data.get('pricePerHour') or service_data.get('pricePerTrip', 0)
    
    if customer_budget:
        if abs(service_price - customer_budget) < 100:
            explanations.append(f"Price matches your budget at ₹{service_price}/{'hour' if service_data.get('pricePerHour') else 'trip'}.")
        elif service_price < customer_budget:
            explanations.append(f"Affordable pricing at ₹{service_price}/{'hour' if service_data.get('pricePerHour') else 'trip'}.")
    
    # Service type match
    if customer_intent.get('serviceType') and service_data.get('type') == customer_intent.get('serviceType'):
        explanations.append(f"Perfect {service_data.get('type')} service for your needs.")
    
    # Default
    if not explanations:
        explanations.append("Good match based on location and availability.")
    
    return " ".join(explanations)


def generate_summary(results: List[Dict], extracted_intent: Dict) -> str:
    """
    Generate summary of search results
    
    Args:
        results: List of matching services
        extracted_intent: Extracted customer intent
        
    Returns:
        Summary string
    """
    count = len(results)
    
    if count == 0:
        return "No services found matching your requirements. Try adjusting your search criteria."
    
    if count == 1:
        top_match = results[0]
        return f"Found 1 perfect match: {top_match.get('providerName', 'Provider')} who is {'in your village' if top_match.get('distance', 10) < 1 else 'nearby'}."
    
    top_match = results[0]
    return f"Found {count} providers matching your requirements. Top match is {top_match.get('providerName', 'Provider')} {'in your village' if top_match.get('distance', 10) < 1 else 'nearby'}."

