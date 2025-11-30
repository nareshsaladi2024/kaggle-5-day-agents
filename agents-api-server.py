"""
ADK Agents API Server for ChatGPT Integration

This server exposes ADK agents as REST API endpoints that can be used with:
- ChatGPT Custom GPTs (via Actions)
- Direct API calls
- Other integrations

Run: python agents-api-server.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os
import importlib.util
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

app = FastAPI(
    title="ADK Agents API",
    description="REST API for Google ADK agents - compatible with ChatGPT",
    version="1.0.0"
)

# Enable CORS for ChatGPT and other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    agent_name: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    conversation_id: Optional[str] = None

# Store for agent instances and runners
agents_cache: Dict[str, Any] = {}
runners_cache: Dict[str, Any] = {}

def load_agent(agent_path: str):
    """Load an ADK agent from a directory path."""
    try:
        # Import the agent module
        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise FileNotFoundError(f"Agent directory not found: {agent_path}")
        
        # Add project root and agent directory to path
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(agent_dir))
        
        # Try importing from agents/ directory first, then Day folders
        agent_name = agent_dir.name
        
        # Try agents/ directory
        agents_dir = project_root / "agents" / agent_name
        if agents_dir.exists() and (agents_dir / "agent.py").exists():
            spec = importlib.util.spec_from_file_location("agent", agents_dir / "agent.py")
            agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agent_module)
        else:
            # Try Day folder structure
            agent_file = agent_dir / "agent.py"
            if agent_file.exists():
                spec = importlib.util.spec_from_file_location("agent", agent_file)
                agent_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(agent_module)
            else:
                raise FileNotFoundError(f"No agent.py found in {agent_path}")
        
        if not hasattr(agent_module, "root_agent"):
            raise AttributeError(f"No root_agent found in {agent_path}")
        
        return agent_module.root_agent
    except Exception as e:
        raise Exception(f"Failed to load agent from {agent_path}: {str(e)}")

def get_agent(agent_name: str):
    """Get or load an agent by name."""
    if agent_name not in agents_cache:
        # Map agent names to paths (try agents/ first, then Day folders)
        agent_paths = {
            "helpful_assistant": "agents/helpful_assistant",
            "sample-agent": "agents/sample-agent",
            "currency_agent": "agents/CurrencyAgent",
            "image_agent": "agents/image_agent",
            "shipping_agent": "agents/shipping_agent",
            "research_agent": "agents/ResearchAgent",
            "customer_support_agent": "agents/CustomerSupportAgent",
            "product_catalog_agent": "agents/ProductCatalogAgent",
            "weather_assistant": "agents/WeatherAssistant",
        }
        
        # Fallback to Day folders if agents/ doesn't exist
        fallback_paths = {
            "helpful_assistant": "Day1a/helpful_assistant",
            "sample-agent": "Day1a/sample-agent",
            "currency_agent": "Day2a/CurrencyAgent",
            "image_agent": "Day2b/image_agent",
            "shipping_agent": "Day2b/shipping_agent",
            "research_agent": "Day4a/ResearchAgent",
            "customer_support_agent": "Day5a/CustomerSupportAgent",
            "product_catalog_agent": "Day5a/ProductCatalogAgent",
            "weather_assistant": "Day5b/WeatherAssistant",
        }
        
        if agent_name not in agent_paths:
            raise ValueError(f"Unknown agent: {agent_name}. Available: {list(agent_paths.keys())}")
        
        # Try agents/ directory first, fallback to Day folders
        agent_path = agent_paths[agent_name]
        if not (project_root / agent_path).exists():
            agent_path = fallback_paths.get(agent_name, agent_paths[agent_name])
        
        agents_cache[agent_name] = load_agent(str(project_root / agent_path))
    
    return agents_cache[agent_name]

def get_runner(agent_name: str):
    """Get or create a runner for an agent."""
    if agent_name not in runners_cache:
        from google.adk.runners import InMemoryRunner
        agent = get_agent(agent_name)
        runners_cache[agent_name] = InMemoryRunner(agent=agent)
    
    return runners_cache[agent_name]

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "ADK Agents API",
        "version": "1.0.0"
    }

@app.get("/agents")
async def list_agents():
    """List all available agents."""
    return {
        "agents": [
            "helpful_assistant",
            "sample-agent",
            "currency_agent",
            "image_agent",
            "shipping_agent",
            "research_agent",
            "customer_support_agent",
            "product_catalog_agent",
            "weather_assistant"
        ]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with an ADK agent.
    
    This endpoint is compatible with ChatGPT Actions/Function calling.
    """
    try:
        # Default to helpful_assistant if not specified
        agent_name = request.agent_name or "helpful_assistant"
        
        # Get runner for the agent
        runner = get_runner(agent_name)
        
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
            agent_name=agent_name,
            conversation_id=request.conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")

@app.post("/chat/{agent_name}")
async def chat_with_agent(agent_name: str, request: ChatRequest):
    """Chat with a specific agent (alternative endpoint)."""
    request.agent_name = agent_name
    return await chat(request)

@app.get("/agents/{agent_name}/info")
async def agent_info(agent_name: str):
    """Get information about a specific agent."""
    try:
        agent = get_agent(agent_name)
        return {
            "name": agent_name,
            "description": getattr(agent, 'description', 'No description'),
            "model": getattr(agent, 'model', 'Unknown'),
            "tools": [tool.name for tool in getattr(agent, 'tools', [])] if hasattr(agent, 'tools') else []
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Agent not found: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Cloud Run sets PORT environment variable
    port = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║         ADK Agents API Server for ChatGPT                ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Server running at: http://{host}:{port}
    API docs: http://{host}:{port}/docs
    Health check: http://{host}:{port}/
    
    Available agents:
    - helpful_assistant
    - sample-agent
    - currency_agent
    - image_agent
    - shipping_agent
    - research_agent
    - customer_support_agent
    - product_catalog_agent
    - weather_assistant
    
    To use with ChatGPT:
    1. Deploy this server (locally or to cloud)
    2. Create a Custom GPT in ChatGPT
    3. Add Action with this API endpoint
    4. Use /chat endpoint for conversations
    """)
    
    uvicorn.run(app, host=host, port=port)

