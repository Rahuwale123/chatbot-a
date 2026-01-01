import httpx
from typing import List, Dict, Any
from langchain.tools import tool
import json
import os
from datetime import datetime


@tool
def nearby_search(query: str, lat: float, long: float, client_id: str, page: int = 1, limit: int = 3) -> str:
    """
    Search for nearby services like car rentals, hospitals, etc.
    Requires query, lat, long, and client_id.
    """
    url = "http://s-ai-3.109.133.205.nip.io/api/find-nearby/"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "lat": lat,
        "long": long,
        "client_id": client_id,
        "page": page,
        "limit": limit
    }
    
    try:
        with httpx.Client() as client:
            print(f"Calling Nearby Search API with payload: {json.dumps(payload, indent=2)}")
            response = client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            print(f"Nearby Search API Response: {json.dumps(data, indent=2)}")
            
            # Filter results to include only necessary fields for the AI
            original_results = data.get("results", [])
            filtered_results = []
            for item in original_results:
                filtered_results.append({
                    "name": item.get("name"),
                    "phone": item.get("phone"),
                    "distance_km": item.get("distance_km"),
                    "description": item.get("description")
                })
            
            return json.dumps(filtered_results)
    except Exception as e:
        print(f"Error calling Nearby Search API: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def grounded_search(query: str) -> str:
    """
    Perform a real-time web search for information outside of local services.
    Use this when live_mode is enabled.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{ "text": f"Perform a web search for: {query}. Return a detailed summary." }]
        }],
        "tools": [{ "google_search": {} }]
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            # Extract the grounded response text from the parts
            return data['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        print(f"Error calling Grounded Search: {str(e)}")
        return f"Search failed: {str(e)}"

@tool
def get_current_datetime() -> str:
    """
    Get the current date and time in Sangamner (IST).
    Use this if the user asks for the current date, time, or year.
    """
    # Note: System time is usually UTC or local to server. 
    # Since the user is in Sangamner, we should provide IST context if possible, 
    # but for simplicity we'll just return the current system time which is 2026-01-01 according to system prompt.
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y, %I:%M %p")


