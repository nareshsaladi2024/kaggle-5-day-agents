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
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

# Configure logging for ADK using utility module
# Add parent directory to path to enable utility imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging - reads ADK_LOG_LEVEL from .env or defaults to DEBUG
setup_adk_logging(agent_name="helpful_assistant", file_only=True)


def get_weather_for_city(city: str = "London") -> Dict[str, Any]:
    """
    Get the current weather for a given city.
    This is a TOOL that the agent can call when users ask about weather.
    
    Args:
        city: Name of the city (default: "London")
    
    Returns:
        Dictionary with weather information including temperature, condition, and description.
    """
    # Mock weather data (can be replaced with real API or MCP server call)
    weather_data = {
        "london": {
            "status": "success",
            "location": "London, UK",
            "temperature": "15°C (59°F)",
            "condition": "Partly Cloudy",
            "description": "Light cloud cover with occasional sunshine",
            "humidity": "65%",
            "wind_speed": "10 km/h",
            "report": "The weather in London is partly cloudy with a temperature of 15°C (59°F). Light cloud cover with occasional sunshine. Humidity is 65% and wind speed is 10 km/h."
        },
        "new york": {
            "status": "success",
            "location": "New York, USA",
            "temperature": "20°C (68°F)",
            "condition": "Sunny",
            "description": "Clear skies with sunshine",
            "humidity": "55%",
            "wind_speed": "12 km/h",
            "report": "The weather in New York is sunny with a temperature of 20°C (68°F). Clear skies with sunshine. Humidity is 55% and wind speed is 12 km/h."
        },
        "tokyo": {
            "status": "success",
            "location": "Tokyo, Japan",
            "temperature": "22°C (72°F)",
            "condition": "Clear",
            "description": "Clear and pleasant",
            "humidity": "60%",
            "wind_speed": "8 km/h",
            "report": "The weather in Tokyo is clear with a temperature of 22°C (72°F). Clear and pleasant conditions. Humidity is 60% and wind speed is 8 km/h."
        }
    }
    
    city_lower = city.lower().strip()
    if city_lower in weather_data:
        return weather_data[city_lower]
    else:
        available_cities = ", ".join([c.title() for c in weather_data.keys()])
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available. Try: {available_cities}",
            "location": city
        }


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
    description="A helpful assistant that can answer general questions and provide weather information.",
    instruction="""You are a helpful assistant.

When users ask about the weather:
1. Use the get_weather_for_city tool to fetch current weather information
2. Respond in a friendly, conversational tone with the weather details
3. If the city isn't available, suggest one of the available cities

Be helpful and concise in your responses.""",
    tools=[get_weather_for_city],  # Note: google_search can't be mixed with custom tools on Vertex AI
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