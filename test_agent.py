import asyncio
import os
from dotenv import load_dotenv
from agent import run_sangamner_agent

load_dotenv()

async def test_agent():
    print("Testing agent...")
    try:
        query = "find car rentals"
        client_id = "test-client"
        lat = 19.5
        long = 74.2
        
        ai_response, results = await run_sangamner_agent(query, client_id, lat, long)
        print("AI Response:", ai_response)
        print("Results:", results)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
