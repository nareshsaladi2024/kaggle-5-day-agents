"""
Basic Session Agent
Simple stateful agent with InMemorySessionService
Based on Day 3a Kaggle notebook
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from utility.logging_config import setup_adk_logging, ensure_debug_logging
    setup_adk_logging(agent_name="basic_session_agent", file_only=True)
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
APP_NAME = os.getenv("APP_NAME", "basic_session_app")
MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")

# Create agent
root_agent = Agent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="text_chat_bot",
    description="A simple text chatbot with session management",
)

# Set up session service (in-memory)
session_service = InMemorySessionService()

# Create runner
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

print(f"✅ Basic session agent initialized!")
print(f"   - App: {APP_NAME}")
print(f"   - Model: {MODEL_NAME}")
print(f"   - Session Service: InMemory (temporary)")

