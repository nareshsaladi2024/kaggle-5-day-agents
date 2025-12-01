"""
Vertex AI Agent Engine Bridge API for ChatGPT/OpenAI/Azure Integration

This server acts as a bridge between:
- ChatGPT Custom GPTs / OpenAI Function Calling / Azure AI
- Vertex AI Agent Engine deployed agents

It wraps Vertex AI Agent Engine agents and exposes them as REST APIs
compatible with ChatGPT Actions, OpenAI Function Calling, and Azure AI.

Run: python vertex-ai-agent-bridge-api.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Vertex AI
import vertexai
from vertexai import agent_engines

app = FastAPI(
    title="Vertex AI Agent Engine Bridge API",
    description="REST API bridge for Vertex AI Agent Engine agents - compatible with ChatGPT, OpenAI, and Azure",
    version="1.0.0"
)

# Enable CORS for ChatGPT, OpenAI, and Azure clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Vertex AI (will be set per request or at startup)
vertex_ai_initialized = False

def init_vertex_ai():
    """Initialize Vertex AI with project and region from environment."""
    global vertex_ai_initialized
    if not vertex_ai_initialized:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "aiagent-capstoneproject")
        region = os.getenv("AGENT_ENGINE_REGION", "us-central1")
        vertexai.init(project=project_id, location=region)
        vertex_ai_initialized = True
        print(f"✓ Vertex AI initialized: project={project_id}, region={region}")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    agent_name: Optional[str] = None
    user_id: Optional[str] = "default_user"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None

# Cache for agent instances
agents_cache: Dict[str, Any] = {}

def get_deployed_agent(agent_name: str):
    """
    Get a deployed agent from Vertex AI Agent Engine.
    
    Args:
        agent_name: Name or ID of the deployed agent
        
    Returns:
        The agent_engines.AgentEngine instance
    """
    init_vertex_ai()
    
    # Check cache first
    if agent_name in agents_cache:
        return agents_cache[agent_name]
    
    # List all deployed agents
    agents_list = list(agent_engines.list())
    
    if not agents_list:
        raise HTTPException(
            status_code=404,
            detail=f"No agents found in Vertex AI Agent Engine. Please deploy agents first."
        )
    
    # Try to find agent by name/ID
    agent = None
    for a in agents_list:
        agent_id = a.resource_name.split('/')[-1]
        if agent_name.lower() == agent_id.lower() or agent_name.lower() in agent_id.lower():
            agent = a
            break
    
    # If not found by name, use first agent or most recent
    if not agent:
        if agent_name:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found. Available agents: {[a.resource_name.split('/')[-1] for a in agents_list]}"
            )
        # Default to first agent
        agent = agents_list[0]
    
    # Cache the agent
    agents_cache[agent_name or agent.resource_name.split('/')[-1]] = agent
    
    return agent

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Vertex AI Agent Engine Bridge API",
        "version": "1.0.0",
        "platforms": ["ChatGPT", "OpenAI", "Azure AI"]
    }

@app.get("/agents")
async def list_agents():
    """List all deployed agents in Vertex AI Agent Engine."""
    try:
        init_vertex_ai()
        agents_list = list(agent_engines.list())
        
        agents_info = []
        for agent in agents_list:
            agent_id = agent.resource_name.split('/')[-1]
            agents_info.append({
                "id": agent_id,
                "resource_name": agent.resource_name,
                "name": agent_id  # Use ID as name
            })
        
        return {
            "agents": agents_info,
            "count": len(agents_info)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with a Vertex AI Agent Engine deployed agent.
    
    This endpoint is compatible with:
    - ChatGPT Custom GPTs (via Actions)
    - OpenAI Function Calling
    - Azure AI Services
    """
    try:
        # Get the deployed agent
        agent = get_deployed_agent(request.agent_name or "")
        agent_id = agent.resource_name.split('/')[-1]
        
        # Use async query for streaming response
        response_parts = []
        async for item in agent.async_stream_query(
            message=request.message,
            user_id=request.user_id or "default_user"
        ):
            # Extract text content from response
            if hasattr(item, "content") and item.content:
                if hasattr(item.content, "parts"):
                    for part in item.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_parts.append(part.text)
                        elif hasattr(part, "function_call"):
                            # Handle function calls if needed
                            response_parts.append(f"[Function call: {part.function_call.name}]")
                        elif hasattr(part, "function_response"):
                            response_parts.append("[Function response received]")
                elif hasattr(item.content, "text"):
                    response_parts.append(item.content.text)
            elif hasattr(item, "text"):
                response_parts.append(item.text)
        
        # Combine all response parts
        response_text = "".join(response_parts) if response_parts else "No response received"
        
        return ChatResponse(
            response=response_text,
            agent_name=agent_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")

@app.post("/chat/{agent_name}")
async def chat_with_agent(agent_name: str, request: ChatRequest):
    """Chat with a specific agent (alternative endpoint)."""
    request.agent_name = agent_name
    return await chat(request)

@app.get("/agents/{agent_name}/info")
async def agent_info(agent_name: str):
    """Get information about a specific deployed agent."""
    try:
        agent = get_deployed_agent(agent_name)
        agent_id = agent.resource_name.split('/')[-1]
        
        return {
            "id": agent_id,
            "resource_name": agent.resource_name,
            "name": agent_id,
            "description": f"Deployed agent from Vertex AI Agent Engine",
            "platform": "Vertex AI Agent Engine"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Agent not found: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Cloud Run sets PORT environment variable
    port = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Vertex AI Agent Engine Bridge API                      ║
    ║   For ChatGPT, OpenAI, and Azure Integration             ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Server running at: http://{host}:{port}
    API docs: http://{host}:{port}/docs
    Health check: http://{host}:{port}/
    
    This bridge connects:
    • Vertex AI Agent Engine (deployed agents)
    • ChatGPT Custom GPTs
    • OpenAI Function Calling
    • Azure AI Services
    
    To use:
    1. Ensure agents are deployed to Vertex AI Agent Engine
    2. Deploy this bridge API (locally or to Cloud Run)
    3. Configure ChatGPT/OpenAI/Azure to use this API endpoint
    4. Use /chat endpoint for conversations
    """)
    
    uvicorn.run(app, host=host, port=port)

