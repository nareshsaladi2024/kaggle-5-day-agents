"""
Weather Assistant Agent
A production-ready agent for deployment to Vertex AI Agent Engine.

This agent provides weather information for cities and demonstrates:
- Agent configuration with tools
- Production deployment patterns
- Vertex AI integration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

import vertexai
from google.adk.agents import Agent

# Load environment variables
load_dotenv()

# Add project root to path for utility imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from utility.logging_config import setup_adk_logging, ensure_debug_logging
    setup_adk_logging(agent_name="weather_assistant", file_only=True)
except ImportError:
    print("Warning: Could not import logging config")

# Initialize Vertex AI
# This is required for Agent Engine deployment
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

if project_id:
    vertexai.init(project=project_id, location=location)
    print(f"✅ Vertex AI initialized: project={project_id}, location={location}")
else:
    print("⚠️  GOOGLE_CLOUD_PROJECT not set. Vertex AI initialization skipped.")


def get_weather(city: str) -> dict:
    """
    Returns weather information for a given city.

    This is a TOOL that the agent can call when users ask about weather.
    In production, this would call a real weather API (e.g., OpenWeatherMap).
    For this demo, we use mock data.

    Args:
        city: Name of the city (e.g., "Tokyo", "New York")

    Returns:
        dict: Dictionary with status and weather report or error message
    """
    # Mock weather database with structured responses
    weather_data = {
        "san francisco": {
            "status": "success",
            "report": "The weather in San Francisco is sunny with a temperature of 72°F (22°C).",
        },
        "new york": {
            "status": "success",
            "report": "The weather in New York is cloudy with a temperature of 65°F (18°C).",
        },
        "london": {
            "status": "success",
            "report": "The weather in London is rainy with a temperature of 58°F (14°C).",
        },
        "tokyo": {
            "status": "success",
            "report": "The weather in Tokyo is clear with a temperature of 70°F (21°C).",
        },
        "paris": {
            "status": "success",
            "report": "The weather in Paris is partly cloudy with a temperature of 68°F (20°C).",
        },
    }

    city_lower = city.lower()
    if city_lower in weather_data:
        return weather_data[city_lower]
    else:
        available_cities = ", ".join([c.title() for c in weather_data.keys()])
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available. Try: {available_cities}",
        }


# Create the root agent
# This is the agent that will be deployed to Agent Engine
root_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",  # Fast, cost-effective Gemini model
    description="A helpful weather assistant that provides weather information for cities.",
    instruction="""
    You are a friendly weather assistant. When users ask about the weather:

    1. Identify the city name from their question
    2. Use the get_weather tool to fetch current weather information
    3. Respond in a friendly, conversational tone
    4. If the city isn't available, suggest one of the available cities

    Be helpful and concise in your responses.
    """,
    tools=[get_weather],
)

print("✅ Weather Assistant Agent created successfully!")
print("   Model: gemini-2.5-flash-lite")
print("   Tool: get_weather()")
print("   Ready for deployment to Agent Engine...")

# Ensure logging is maintained after agent creation
try:
    ensure_debug_logging(agent_name="weather_assistant")
except NameError:
    pass

