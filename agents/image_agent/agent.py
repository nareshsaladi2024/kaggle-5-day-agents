import uuid
from google.genai import types
import sys
from pathlib import Path
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
import base64
import json

# Load environment variables from .env file
load_dotenv()

# Configure logging for ADK using utility module
# Add project root to path to enable utility imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging - reads ADK_LOG_LEVEL from .env or defaults to DEBUG
setup_adk_logging(agent_name="image_agent", file_only=True)
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)
# MCP integration with Everything Server
mcp_image_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@modelcontextprotocol/server-everything",
            ],
            tool_filter=["getTinyImage"],
        ),
        timeout=30,
    )
)

print("✅ MCP Tool created")

# Function to format image response for ADK web display
def format_image_for_display(image_response: str) -> str:
    """
    Format image response from MCP tool for ADK web display.
    The MCP getTinyImage tool returns image data that needs to be formatted as markdown.
    
    Args:
        image_response: Response from getTinyImage tool (may be JSON string or dict)
        
    Returns:
        Formatted markdown string with embedded image using data URI
    """
    try:
        # Parse JSON if it's a string
        if isinstance(image_response, str):
            try:
                parsed = json.loads(image_response)
                image_response = parsed
            except:
                # If not JSON, might be base64 directly
                pass
        
        # Extract image data from various possible response formats
        image_data = None
        
        if isinstance(image_response, dict):
            # Try different possible keys
            if "content" in image_response:
                content = image_response["content"]
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "image" and "data" in item:
                                image_data = item["data"]
                                break
                            elif "data" in item:
                                image_data = item["data"]
                                break
                elif isinstance(content, dict):
                    if content.get("type") == "image" and "data" in content:
                        image_data = content["data"]
                    elif "data" in content:
                        image_data = content["data"]
            elif "data" in image_response:
                image_data = image_response["data"]
            elif "image" in image_response:
                image_data = image_response["image"]
            elif "response" in image_response:
                # Recursively check
                return format_image_for_display(image_response["response"])
        elif isinstance(image_response, str):
            # Might be base64 directly
            image_data = image_response
        
        if image_data:
            # Verify and format
            try:
                # Decode to verify it's valid base64
                decoded = base64.b64decode(image_data)
                
                # Determine image format
                if decoded.startswith(b'\xff\xd8'):
                    fmt = "jpeg"
                elif decoded.startswith(b'\x89PNG'):
                    fmt = "png"
                elif decoded.startswith(b'GIF'):
                    fmt = "gif"
                elif decoded.startswith(b'WEBP'):
                    fmt = "webp"
                else:
                    fmt = "png"  # Default
                
                # Return markdown with data URI
                return f"![Generated Image](data:image/{fmt};base64,{image_data})"
            except Exception as e:
                return f"Image data received but could not be decoded: {str(e)}"
        
        return "Image generation completed, but image data not found in expected format."
    
    except Exception as e:
        return f"Error formatting image: {str(e)}"

# Create image agent with MCP integration
# Updated instruction to format image responses for web display
image_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="image_agent",
    instruction="""You are an image generation assistant. When users request images:

CRITICAL: When the getTinyImage tool returns a response, you MUST:
1. Extract the base64-encoded image data from the tool response
2. The response may be in JSON format with keys like "content", "data", or "image"
3. Look for base64-encoded image data in the response structure
4. Format it EXACTLY as: ![description](data:image/png;base64,<base64_data_here>)
5. Replace <base64_data_here> with the actual base64 string from the tool response
6. Include this formatted image markdown in your response

Example: If the tool returns {"content": [{"type": "image", "data": "iVBORw0KG..."}]}, 
extract "iVBORw0KG..." and format as: ![Generated Image](data:image/png;base64,iVBORw0KG...)

IMPORTANT: 
- Always include the full base64 image data in your response
- Do NOT just say "here is the image" - you MUST include the actual image markdown
- The ADK web interface will automatically render images formatted this way
- If you cannot find the image data, describe what the tool returned so we can debug""",
    tools=[mcp_image_server],
)

print("✅ image_agent created.")

# Define root_agent at module level for ADK web server
root_agent = image_agent

# Ensure logging is maintained after agent creation
ensure_debug_logging(agent_name="image_agent")