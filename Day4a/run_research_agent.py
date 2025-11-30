"""
Run the Research Paper Finder Agent with observability.

This script demonstrates:
- Running agent with LoggingPlugin for observability
- Debugging agent behavior through logs

Usage:
    python run_research_agent.py
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.adk.runners import InMemoryRunner
from google.adk.plugins.logging_plugin import LoggingPlugin

# Import agent
from Day4a.ResearchAgent.agent import research_agent


async def main():
    """Run the research agent with observability."""
    print("=" * 60)
    print("Research Paper Finder Agent - Observability Demo")
    print("=" * 60)
    print("\nThis demo shows:")
    print("• LoggingPlugin for comprehensive observability")
    print("• Agent execution traces")
    print("• Tool calls and responses")
    print("=" * 60)

    # Create runner with LoggingPlugin
    runner = InMemoryRunner(
        agent=research_agent,
        plugins=[LoggingPlugin()],  # Add observability plugin
    )

    print("\n🚀 Running agent with LoggingPlugin...")
    print("📊 Watch the comprehensive logging output below:\n")

    query = "Find recent papers on quantum computing"
    print(f"👤 User: {query}\n")
    print("🤖 Agent Response:")
    print("-" * 60)

    response = await runner.run_debug(query)

    print("-" * 60)
    print("\n✅ Agent execution completed!")
    print("\nObservability Features Demonstrated:")
    print("• User message logging")
    print("• Agent invocation tracking")
    print("• LLM request/response logging")
    print("• Tool call execution logging")
    print("• Complete execution traces")


if __name__ == "__main__":
    asyncio.run(main())

