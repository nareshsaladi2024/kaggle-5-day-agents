"""
Script to run the image_agent and display images from function responses.

This script:
1. Runs the image_agent with a user query
2. Processes the streaming response
3. Extracts and displays images from function responses
"""

import asyncio
import base64
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.adk.runners import InMemoryRunner
from Day2b.image_agent.agent import image_agent

# For Jupyter notebook display
try:
    from IPython.display import display, Image as IPImage
    IN_JUPYTER = True
except ImportError:
    IN_JUPYTER = False


async def run_agent_and_display_images(query: str):
    """
    Run the image agent and display any images returned in function responses.
    
    Args:
        query: The user query/prompt for the agent
    """
    runner = InMemoryRunner(agent=image_agent)
    
    print(f"Running agent with query: {query}\n")
    
    # Run the agent and get streaming response
    response = await runner.run_debug(query)
    
    # Process the response to extract and display images
    if hasattr(response, 'events') or hasattr(response, 'stream'):
        # Handle streaming response
        events = getattr(response, 'events', []) or getattr(response, 'stream', [])
        
        for event in events:
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'function_response') and part.function_response:
                            # Extract images from function response
                            function_response = part.function_response
                            
                            # Handle different response formats
                            if hasattr(function_response, 'response'):
                                response_data = function_response.response
                                
                                # If response is a dict with content list
                                if isinstance(response_data, dict):
                                    content = response_data.get("content", [])
                                    for item in content:
                                        if isinstance(item, dict) and item.get("type") == "image":
                                            image_data = item.get("data")
                                            if image_data:
                                                display_image(image_data)
                                
                                # If response is a list
                                elif isinstance(response_data, list):
                                    for item in response_data:
                                        if isinstance(item, dict) and item.get("type") == "image":
                                            image_data = item.get("data")
                                            if image_data:
                                                display_image(image_data)
                                
                                # If response contains base64 image data directly
                                elif isinstance(response_data, str):
                                    # Try to decode if it's base64
                                    try:
                                        image_bytes = base64.b64decode(response_data)
                                        display_image(image_bytes, is_bytes=True)
                                    except:
                                        pass
    
    # Also check the final response text
    if hasattr(response, 'text'):
        print(f"\nAgent Response: {response.text}")
    elif hasattr(response, 'content'):
        print(f"\nAgent Response: {response.content}")
    
    return response


def display_image(image_data, is_bytes=False):
    """
    Display an image from base64 data or bytes.
    
    Args:
        image_data: Base64 encoded string or bytes
        is_bytes: If True, image_data is already bytes, not base64 string
    """
    try:
        if is_bytes:
            image_bytes = image_data
        else:
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(image_data)
        
        if IN_JUPYTER:
            # Display in Jupyter notebook
            display(IPImage(data=image_bytes))
        else:
            # Save to file for non-Jupyter environments
            output_dir = Path(__file__).parent / "output_images"
            output_dir.mkdir(exist_ok=True)
            
            import uuid
            filename = output_dir / f"image_{uuid.uuid4().hex[:8]}.png"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Image saved to: {filename}")
    
    except Exception as e:
        print(f"❌ Error displaying image: {e}")


async def main():
    """Main function to run the agent."""
    # Example query - modify as needed
    query = "Generate an image of a sunset over the ocean"
    
    response = await run_agent_and_display_images(query)
    return response


if __name__ == "__main__":
    # Run the agent
    asyncio.run(main())

