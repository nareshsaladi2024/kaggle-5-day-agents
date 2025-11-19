from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types
import vertexai
import os
import asyncio
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Configure logging for ADK using utility module
# Add parent directory to path to enable utility imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging - reads ADK_LOG_LEVEL from .env or defaults to DEBUG
setup_adk_logging(agent_name="helpful_assistant", file_only=True)

# Define root_agent at module level for ADK web server
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,  # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504]  # Retry on these HTTP errors
)

root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
)

# Ensure logging is maintained after agent creation
ensure_debug_logging(agent_name="helpful_assistant")


async def main():
    print("✅ ADK components imported successfully.")
    print("✅ Root Agent defined.")
    
    runner = InMemoryRunner(agent=root_agent)
    print("✅ Runner created.")
    
    response = await runner.run_debug(
        "What is Agent Development Kit from Google? What languages is the SDK available in?"
    )
    
    return response

    #response = await runner.run_debug("What's the weather in London?")


if __name__ == "__main__":
    asyncio.run(main())