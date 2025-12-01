"""
Weather Assistant API Server

FastAPI server that wraps the WeatherAssistant ADK agent and exposes it as a REST API.
This allows the agent to be deployed to Docker Desktop and Cloud Run.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

app = FastAPI(
    title="Weather Assistant API",
    description="REST API for WeatherAssistant ADK agent",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None

# Cache for agent and runner
agent_cache = None
runner_cache = None

def get_agent():
    """Get or load the WeatherAssistant agent."""
    global agent_cache
    if agent_cache is None:
        try:
            # Import the agent
            from WeatherAssistant.agent import root_agent
            agent_cache = root_agent
            print("✅ WeatherAssistant agent loaded successfully")
        except Exception as e:
            raise Exception(f"Failed to load agent: {str(e)}")
    return agent_cache

def get_runner():
    """Get or create a runner for the agent."""
    global runner_cache
    if runner_cache is None:
        try:
            from google.adk.runners import InMemoryRunner
            agent = get_agent()
            runner_cache = InMemoryRunner(agent=agent)
            print("✅ Runner created successfully")
        except Exception as e:
            raise Exception(f"Failed to create runner: {str(e)}")
    return runner_cache

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Weather Assistant API",
        "version": "1.0.0",
        "agent": "WeatherAssistant"
    }

@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run."""
    try:
        # Try to get agent to verify it's loaded
        get_agent()
        return {
            "status": "healthy",
            "agent": "loaded"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the WeatherAssistant agent.
    
    This endpoint is compatible with ChatGPT Actions and other integrations.
    """
    try:
        # Get runner
        runner = get_runner()
        
        # Run the agent
        response = await runner.run(request.message)
        
        # Extract text response
        if hasattr(response, 'messages') and response.messages:
            response_text = response.messages[-1].content if hasattr(response.messages[-1], 'content') else str(response.messages[-1])
        elif hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        return ChatResponse(
            response=response_text,
            conversation_id=request.conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")

@app.get("/info")
async def info():
    """Get information about the agent."""
    try:
        agent = get_agent()
        return {
            "name": getattr(agent, 'name', 'weather_assistant'),
            "description": getattr(agent, 'description', 'Weather assistant agent'),
            "model": getattr(agent, 'model', 'Unknown'),
            "tools": [tool.name if hasattr(tool, 'name') else str(tool) for tool in getattr(agent, 'tools', [])]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Cloud Run sets PORT environment variable
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║         Weather Assistant API Server                      ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Server running at: http://{host}:{port}
    API docs: http://{host}:{port}/docs
    Health check: http://{host}:{port}/health
    
    Agent: WeatherAssistant
    Model: gemini-2.5-flash-lite
    
    To use:
    - POST /chat with {{"message": "What's the weather in London?"}}
    - GET /info for agent information
    """)
    
    uvicorn.run(app, host=host, port=port)

