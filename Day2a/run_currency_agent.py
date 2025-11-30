"""
Run the Currency Converter Agent.

This script demonstrates:
- Basic currency agent with function tools
- Enhanced currency agent with agent tools (calculation delegation)

Usage:
    python run_currency_agent.py
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import agents
from Day2a.CurrencyAgent.agent import (
    currency_agent,
    enhanced_currency_agent,
)


async def test_basic_currency_agent():
    """Test the basic currency agent."""
    print("=" * 60)
    print("Basic Currency Agent Test")
    print("=" * 60)

    runner = InMemoryRunner(agent=currency_agent)
    query = "I want to convert 500 US Dollars to Euros using my Platinum Credit Card. How much will I receive?"

    print(f"\n👤 User: {query}\n")
    print("🤖 Agent Response:")
    print("-" * 60)

    response = await runner.run_debug(query)
    print("-" * 60)


async def test_enhanced_currency_agent():
    """Test the enhanced currency agent with calculation delegation."""
    print("\n" + "=" * 60)
    print("Enhanced Currency Agent Test (with Calculation Agent)")
    print("=" * 60)

    runner = InMemoryRunner(agent=enhanced_currency_agent)
    query = "Convert 1,250 USD to INR using a Bank Transfer. Show me the precise calculation."

    print(f"\n👤 User: {query}\n")
    print("🤖 Agent Response:")
    print("-" * 60)

    response = await runner.run_debug(query)
    print("-" * 60)


async def main():
    """Run all tests."""
    print("\n🚀 Currency Converter Agent Demo")
    print("=" * 60)
    print("This demo shows:")
    print("1. Basic agent with custom function tools")
    print("2. Enhanced agent that delegates calculations to a specialist agent")
    print("=" * 60)

    # Test basic agent
    await test_basic_currency_agent()

    # Test enhanced agent
    await test_enhanced_currency_agent()

    print("\n✅ All tests completed!")
    print("\nKey Takeaways:")
    print("• Function Tools: Python functions become agent tools")
    print("• Agent Tools: Other agents can be used as tools")
    print("• Code Execution: Reliable calculations using Python code")


if __name__ == "__main__":
    asyncio.run(main())

