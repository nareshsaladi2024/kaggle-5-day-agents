"""
Demo script to test A2A communication between Customer Support Agent and Product Catalog Agent.

This script:
1. Tests the A2A communication between agents
2. Demonstrates how Customer Support Agent queries Product Catalog Agent
3. Shows the transparent agent-to-agent communication

Prerequisites:
- Product Catalog Agent server must be running (run_product_catalog_server.py)

Usage:
    python run_a2a_demo.py
"""

import asyncio
import uuid
import sys
from pathlib import Path
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the customer support agent
from Day5a.CustomerSupportAgent.agent import customer_support_agent


async def test_a2a_communication(user_query: str):
    """
    Test the A2A communication between Customer Support Agent and Product Catalog Agent.

    This function:
    1. Creates a new session for this conversation
    2. Sends the query to the Customer Support Agent
    3. Support Agent communicates with Product Catalog Agent via A2A
    4. Displays the response

    Args:
        user_query: The question to ask the Customer Support Agent
    """
    # Setup session management (required by ADK)
    session_service = InMemorySessionService()

    # Session identifiers
    app_name = "support_app"
    user_id = "demo_user"
    # Use unique session ID for each test to avoid conflicts
    session_id = f"demo_session_{uuid.uuid4().hex[:8]}"

    # CRITICAL: Create session BEFORE running agent (synchronous, not async!)
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    # Create runner for the Customer Support Agent
    # The runner manages the agent execution and session state
    runner = Runner(
        agent=customer_support_agent, app_name=app_name, session_service=session_service
    )

    # Create the user message
    test_content = types.Content(parts=[types.Part(text=user_query)])

    # Display query
    print(f"\n👤 Customer: {user_query}")
    print(f"\n🎧 Support Agent response:")
    print("-" * 60)

    # Run the agent asynchronously (handles streaming responses and A2A communication)
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=test_content
    ):
        # Print final response only (skip intermediate events)
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text"):
                    print(part.text)

    print("-" * 60)


async def main():
    """Run demo tests."""
    print("=" * 60)
    print("A2A Communication Demo")
    print("=" * 60)
    print("\n⚠️  Make sure Product Catalog Agent server is running!")
    print("   Run: python run_product_catalog_server.py")
    print("=" * 60)
    
    # Test 1: Single product inquiry
    print("\n📦 Test 1: Single Product Inquiry")
    await test_a2a_communication("Can you tell me about the iPhone 15 Pro? Is it in stock?")
    
    # Test 2: Compare multiple products
    print("\n📦 Test 2: Compare Multiple Products")
    await test_a2a_communication(
        "I'm looking for a laptop. Can you compare the Dell XPS 15 and MacBook Pro 14 for me?"
    )
    
    # Test 3: Specific product inquiry
    print("\n📦 Test 3: Specific Product Inquiry")
    await test_a2a_communication(
        "Do you have the Sony WH-1000XM5 headphones? What's the price?"
    )
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())

