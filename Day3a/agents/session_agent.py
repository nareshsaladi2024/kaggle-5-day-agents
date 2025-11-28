"""
Session Management Agent
Demonstrates stateful agents with session management using ADK
Based on Day 3a Kaggle notebook
"""

from typing import Any, Dict
from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

# Add parent directory to path for utility imports
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from utility.logging_config import setup_adk_logging, ensure_debug_logging
    setup_adk_logging(agent_name="session_agent", file_only=True)
except ImportError:
    print("Warning: Could not import logging config")

# Configure retry options
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Configuration
APP_NAME = os.getenv("APP_NAME", "session_app")
USER_ID = os.getenv("USER_ID", "default")
MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")

# Session state management tools
def save_userinfo(
    tool_context: ToolContext, user_name: str, country: str
) -> Dict[str, Any]:
    """
    Tool to record and save user name and country in session state.
    
    Args:
        user_name: The username to store in session state
        country: The name of the user's country
    """
    tool_context.state["user:name"] = user_name
    tool_context.state["user:country"] = country
    return {"status": "success", "message": f"Saved user info: {user_name} from {country}"}


def retrieve_userinfo(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool to retrieve user name and country from session state.
    """
    user_name = tool_context.state.get("user:name", "Username not found")
    country = tool_context.state.get("user:country", "Country not found")
    return {"status": "success", "user_name": user_name, "country": country}


# Create agent with session state tools
root_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="session_chat_bot",
    description="""A text chatbot with session management capabilities.
    Tools for managing user context:
    * To record username and country when provided use `save_userinfo` tool. 
    * To fetch username and country when required use `retrieve_userinfo` tool.
    """,
    tools=[save_userinfo, retrieve_userinfo],
)

# Session service configuration
SESSION_SERVICE_TYPE = os.getenv("SESSION_SERVICE_TYPE", "inmemory")  # inmemory or database
DB_URL = os.getenv("DB_URL", "sqlite:///session_data.db")

if SESSION_SERVICE_TYPE == "database":
    session_service = DatabaseSessionService(db_url=DB_URL)
    print(f"✅ Using DatabaseSessionService: {DB_URL}")
else:
    session_service = InMemorySessionService()
    print("✅ Using InMemorySessionService (temporary)")

# Create runner
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

print(f"✅ Session agent initialized!")
print(f"   - App: {APP_NAME}")
print(f"   - Model: {MODEL_NAME}")
print(f"   - Session Service: {session_service.__class__.__name__}")

