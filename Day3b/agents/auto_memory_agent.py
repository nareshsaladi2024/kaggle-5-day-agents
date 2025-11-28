"""
Automatic Memory Storage Agent
Demonstrates automatic memory storage using callbacks
Based on Day 3b Kaggle notebook
"""

from typing import Any, Dict
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import preload_memory
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
    setup_adk_logging(agent_name="auto_memory_agent", file_only=True)
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
APP_NAME = os.getenv("APP_NAME", "AutoMemoryApp")
USER_ID = os.getenv("USER_ID", "demo_user")
MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")

# Session and memory services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# Callback for automatic memory storage
async def auto_save_to_memory(callback_context):
    """
    Automatically save session to memory after each agent turn.
    This callback is triggered after the agent completes processing.
    """
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Create agent with preload_memory (proactive memory loading)
root_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="AutoMemoryAgent",
    instruction="Answer user questions in simple words. Memory is automatically loaded before each turn.",
    tools=[preload_memory],
    after_agent_callback=auto_save_to_memory,  # Automatically save to memory after each turn
)

# Create runner
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)

print(f"✅ Auto memory agent initialized!")
print(f"   - App: {APP_NAME}")
print(f"   - Model: {MODEL_NAME}")
print(f"   - Automatic memory storage: Enabled (after_agent_callback)")
print(f"   - Memory retrieval: Proactive (preload_memory)")

