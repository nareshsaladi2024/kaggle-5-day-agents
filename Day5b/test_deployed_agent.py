"""
Test a deployed Weather Assistant Agent on Vertex AI Agent Engine.

This script connects to a deployed agent and sends test queries.

Prerequisites:
- Agent must be deployed to Agent Engine (use deploy_to_agent_engine.py)
- Google Cloud credentials configured
- Vertex AI initialized

Usage:
    python test_deployed_agent.py --project-id YOUR_PROJECT_ID --region us-east4
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv

import vertexai
from vertexai import agent_engines

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_agent(project_id: str, region: str, query: str, user_id: str = "test_user"):
    """
    Test a deployed agent with a query.

    Args:
        project_id: Google Cloud project ID
        region: Deployment region
        query: Query to send to the agent
        user_id: User ID for the session
    """
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=region)

    print("=" * 60)
    print("Testing Deployed Weather Assistant Agent")
    print("=" * 60)
    print(f"Project ID: {project_id}")
    print(f"Region: {region}")
    print(f"Query: {query}")
    print("=" * 60)

    # Get the most recently deployed agent
    agents_list = list(agent_engines.list())
    if not agents_list:
        print("❌ No agents found. Please deploy first using deploy_to_agent_engine.py")
        return

    remote_agent = agents_list[0]  # Get the first (most recent) agent
    print(f"\n✅ Connected to deployed agent: {remote_agent.resource_name}\n")

    print(f"👤 User: {query}")
    print(f"\n🤖 Agent Response:")
    print("-" * 60)

    # Stream the response
    async for item in remote_agent.async_stream_query(message=query, user_id=user_id):
        # Print different types of responses
        if hasattr(item, "content") and item.content:
            if hasattr(item.content, "parts"):
                for part in item.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(part.text, end="", flush=True)
                    elif hasattr(part, "function_call"):
                        print(f"\n[Function call: {part.function_call.name}]", end="", flush=True)
                    elif hasattr(part, "function_response"):
                        print(f"\n[Function response received]", end="", flush=True)

    print("\n" + "-" * 60)
    print("\n✅ Test completed!")


async def run_demo_tests(project_id: str, region: str):
    """Run a series of demo tests."""
    print("\n🧪 Running Demo Tests\n")

    test_queries = [
        "What is the weather in Tokyo?",
        "Can you tell me about the weather in London?",
        "What's the weather like in San Francisco?",
        "I'm planning a trip to Paris. What's the weather there?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_queries)}")
        print(f"{'='*60}")
        await test_agent(project_id, region, query, user_id=f"demo_user_{i}")
        print()  # Add spacing between tests


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test deployed agent on Vertex AI Agent Engine")
    parser.add_argument(
        "--project-id",
        type=str,
        default=os.getenv("GOOGLE_CLOUD_PROJECT"),
        help="Google Cloud project ID (default: from GOOGLE_CLOUD_PROJECT env var)",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=os.getenv("AGENT_ENGINE_REGION", "us-east4"),
        help="Deployment region (default: us-east4)",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Query to send to the agent (default: run demo tests)",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="test_user",
        help="User ID for the session (default: test_user)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo tests instead of single query",
    )

    args = parser.parse_args()

    if not args.project_id:
        print("❌ Error: --project-id is required or set GOOGLE_CLOUD_PROJECT env var")
        sys.exit(1)

    if args.demo or not args.query:
        asyncio.run(run_demo_tests(args.project_id, args.region))
    else:
        asyncio.run(test_agent(args.project_id, args.region, args.query, args.user_id))


if __name__ == "__main__":
    main()

