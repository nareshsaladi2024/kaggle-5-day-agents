# ADK Discovery Wrapper
# This file makes all agents in Day3a discoverable by ADK web server

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import the session agent
try:
    from Day3a.agents.session_agent import root_agent
    # root_agent is now available for ADK discovery
except ImportError as e:
    print(f"Warning: Could not import agent from Day3a.agents.session_agent : {e}")
    # Create a fallback agent
    from google.adk.agents import Agent
    from google.adk.models.google_llm import Gemini
    root_agent = Agent(
        name="Day3a",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="Wrapper agent for Day3a - import failed",
        instruction="This is a wrapper agent. The actual agent could not be loaded."
    )

