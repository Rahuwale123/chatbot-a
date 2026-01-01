import os
import json
from typing import List, Dict, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain import hub
from tools import nearby_search, grounded_search, get_current_datetime
from schemas import NearbyItem


def get_agent_executor(client_id: str, lat: float, long: float, live_mode: bool = False):

    # Bind context to the tool
    # We create a wrapper to ensure the agent doesn't have to provide lat/long/client_id
    def search_wrapper(query: str):
        return nearby_search.invoke({
            "query": query,
            "lat": lat,
            "long": long,
            "client_id": client_id
        })

    # Note: For better agent control, we can redefine the tool or use partials
    # In this case, we'll try to let the agent know these parameters are fixed
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0,
        convert_system_message_to_human=True
    )
    
    tools = [nearby_search, get_current_datetime]
    if live_mode:
        tools.append(grounded_search)

    
    prompt = hub.pull("hwchase17/structured-chat-agent")

    
    agent = create_structured_chat_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )
    
    return agent_executor

async def run_sangamner_agent(query: str, client_id: str, lat: float, long: float, history: List[Dict[str, str]] = None, live_mode: bool = False) -> Tuple[str, List[NearbyItem]]:
    # Create the executor with the specific context
    agent_executor = get_agent_executor(client_id, lat, long, live_mode)

    
    # Format history for the prompt
    history_str = ""
    if history:
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])

    input_str = f"""
    Previous Conversation:
    {history_str}

    Current User Query: {query}
    Context: Latitude {lat}, Longitude {long}, Client ID {client_id}.
    You must use the nearby_search tool if searching for services. 
    Pass the context parameters (lat, long, client_id) to the tool.
    
    IMPORTANT: 
    - Only use the `nearby_search` tool if the user explicitly asks to find something in Sangamner or expresses a need for a local service. 
    - {"Only use the `grounded_search` tool if `live_mode` is enabled and the user asks for real-time information or something outside local services." if live_mode else ""}
    - Do NOT use tools for simple greetings, introductions, or casual conversation (e.g., "hi", "I am Rahul"). In these cases, just respond naturally and wait for a specific request.

    - Do not list the names, phone numbers, or details of the services found in your text response. 
    - Just give a very brief and natural summary or greeting (e.g., "I found 3 hospitals nearby."). 
    - The details will be shown in a separate UI component. 
    - Take into account the previous conversation if relevant.
    """
    
    response = agent_executor.invoke({"input": input_str})

    
    ai_text = response.get("output", "")
    
    # Extract results from intermediate steps
    results = []
    intermediate_steps = response.get("intermediate_steps", [])
    for action, observation in intermediate_steps:
        if action.tool == "nearby_search":
            try:
                obs_data = json.loads(observation)
                if isinstance(obs_data, list):
                    for item in obs_data:
                        results.append(NearbyItem(
                            name=item.get("name", "N/A"),
                            phone_number=item.get("phone") or item.get("number"),
                            distance=str(item.get("distance_km", "N/A"))
                        ))
            except:
                pass
                
    return ai_text, results[:3] # Limit to 3 results as requested
