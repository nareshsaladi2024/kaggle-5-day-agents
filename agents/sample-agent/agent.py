from google.adk.agents.llm_agent import Agent
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

# Configure logging for ADK using utility module
# Add parent directory to path to enable utility imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging - reads ADK_LOG_LEVEL from .env or defaults to DEBUG
setup_adk_logging(agent_name="sample-agent", file_only=True)


def get_weather_in_london() -> Dict[str, Any]:
    """
    Get the current weather in London, UK.
    This is a TOOL that the agent can call when users ask about weather in London.
    
    Returns:
        Dictionary with weather information including temperature, condition, and description.
    """
    # Mock weather data (can be replaced with real API or MCP server call)
    return {
        "status": "success",
        "location": "London, UK",
        "temperature": "15°C (59°F)",
        "condition": "Partly Cloudy",
        "description": "Light cloud cover with occasional sunshine",
        "humidity": "65%",
        "wind_speed": "10 km/h",
        "report": "The weather in London is partly cloudy with a temperature of 15°C (59°F). Light cloud cover with occasional sunshine. Humidity is 65% and wind speed is 10 km/h."
    }

# Define root_agent at module level for ADK web server
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='sample-agent',
    description='A helpful assistant for user questions with weather information capabilities.',
    instruction='''Answer user questions to the best of your knowledge. 

When users ask about the weather in London:
1. Use the get_weather_in_london tool to fetch current weather information
2. Respond in a friendly, conversational tone with the weather details

Be helpful and concise in your responses.''',
    tools=[get_weather_in_london],
)

# Ensure logging is maintained after agent creation
ensure_debug_logging(agent_name="sample-agent")
