"""
Jupyter Notebook cell code for running image_agent and displaying images.

Copy this code into a Jupyter notebook cell to run the agent interactively.
"""

# Cell 1: Import and setup
import asyncio
import base64
from pathlib import Path
import sys

# Add project root to path
project_root = Path().resolve().parent
sys.path.insert(0, str(project_root))

from google.adk.runners import InMemoryRunner
from Day2b.image_agent.agent import image_agent
from IPython.display import display, Image as IPImage

# Cell 2: Run agent and process response
async def run_agent(query: str):
    """Run the agent with a query and return the response."""
    runner = InMemoryRunner(agent=image_agent)
    response = await runner.run_debug(query)
    return response

# Run the agent (modify query as needed)
query = "Generate an image of a sunset over the ocean"
response = await run_agent(query)

# Cell 3: Process response and display images
# This is the code from your notebook selection
for event in response:
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "function_response") and part.function_response:
                for item in part.function_response.response.get("content", []):
                    if item.get("type") == "image":
                        display(IPImage(data=base64.b64decode(item["data"])))

