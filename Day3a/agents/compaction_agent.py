"""
Context Compaction Agent
Demonstrates automatic context compaction for long conversations
Based on Day 3a Kaggle notebook
"""

from google.adk.agents import LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.sessions import DatabaseSessionService
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
    setup_adk_logging(agent_name="compaction_agent", file_only=True)
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
APP_NAME = os.getenv("APP_NAME", "compaction_app")
MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")
DB_URL = os.getenv("DB_URL", "sqlite:///compaction_data.db")

# Compaction configuration
COMPACTION_INTERVAL = int(os.getenv("COMPACTION_INTERVAL", "3"))
OVERLAP_SIZE = int(os.getenv("OVERLAP_SIZE", "1"))

# Create agent
chatbot_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="compaction_chat_bot",
    description="A text chatbot with automatic context compaction for long conversations",
)

# Create app with compaction config
compaction_app = App(
    name=APP_NAME,
    root_agent=chatbot_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=COMPACTION_INTERVAL,
        overlap_size=OVERLAP_SIZE,
    ),
)

# Set up session service
session_service = DatabaseSessionService(db_url=DB_URL)

# Create runner
runner = Runner(
    app=compaction_app,
    session_service=session_service
)

print(f"✅ Compaction agent initialized!")
print(f"   - App: {APP_NAME}")
print(f"   - Compaction interval: {COMPACTION_INTERVAL} turns")
print(f"   - Overlap size: {OVERLAP_SIZE}")
print(f"   - Database: {DB_URL}")

