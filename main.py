import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from schemas import ChatRequest, ChatResponse
from agent import run_sangamner_agent

load_dotenv()

app = FastAPI(title="Sangamner AI API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ai", response_model=ChatResponse)
async def ai_endpoint(request: ChatRequest):
    try:
        ai_response, results = await run_sangamner_agent(
            query=request.query,
            client_id=request.client_id,
            lat=request.lat,
            long=request.long,
            history=[{"role": m.role, "content": m.content} for m in request.history] if request.history else [],
            live_mode=request.live_mode
        )
        
        return ChatResponse(
            ai_response=ai_response,
            results=results
        )
    except Exception as e:
        # In a real app we'd log this
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
