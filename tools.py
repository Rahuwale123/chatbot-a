import httpx
from typing import List, Dict, Any
from langchain.tools import tool
import json

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
