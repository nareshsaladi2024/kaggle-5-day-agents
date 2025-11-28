"""
Memory Management Agent
Demonstrates long-term memory storage and retrieval using ADK
Based on Day 3b Kaggle notebook
"""

from typing import Any, Dict
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
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
    setup_adk_logging(agent_name="memory_agent", file_only=True)
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
APP_NAME = os.getenv("APP_NAME", "MemoryDemoApp")
USER_ID = os.getenv("USER_ID", "demo_user")
MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")

# Session service configuration
SESSION_SERVICE_TYPE = os.getenv("SESSION_SERVICE_TYPE", "inmemory")  # inmemory or database
DB_URL = os.getenv("DB_URL", "sqlite:///memory_data.db")

if SESSION_SERVICE_TYPE == "database":
    session_service = DatabaseSessionService(db_url=DB_URL)
    print(f"✅ Using DatabaseSessionService: {DB_URL}")
else:
    session_service = InMemorySessionService()
    print("✅ Using InMemorySessionService (temporary)")

# Memory service (InMemoryMemoryService for development/testing)
# For production, use VertexAiMemoryBankService (covered in Day 5)
memory_service = InMemoryMemoryService()
print("✅ Using InMemoryMemoryService (keyword matching, no persistence)")

# Create agent with memory retrieval tool
# Options: load_memory (reactive) or preload_memory (proactive)
MEMORY_MODE = os.getenv("MEMORY_MODE", "reactive")  # reactive or proactive

if MEMORY_MODE == "proactive":
    memory_tool = preload_memory
    memory_description = "Automatically loads memory before every turn"
else:
    memory_tool = load_memory
    memory_description = "Agent decides when to search memory"

root_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="MemoryDemoAgent",
    instruction="Answer user questions in simple words. Use memory tools to recall past conversations when needed.",
    tools=[memory_tool],
)

# Create runner with both session and memory services
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)

print(f"✅ Memory agent initialized!")
print(f"   - App: {APP_NAME}")
print(f"   - Model: {MODEL_NAME}")
print(f"   - Session Service: {session_service.__class__.__name__}")
print(f"   - Memory Service: {memory_service.__class__.__name__}")
print(f"   - Memory Mode: {MEMORY_MODE} ({memory_description})")


