"""
Research Paper Finder Agent
Demonstrates agent observability, debugging, and logging.

This agent shows:
- How to debug agent failures using logs
- How to use LoggingPlugin for production observability
- How to identify and fix agent issues
"""

import os
import sys
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

# Load environment variables
load_dotenv()

# Add project root to path for utility imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from utility.logging_config import setup_adk_logging, ensure_debug_logging
    setup_adk_logging(agent_name="research_agent", file_only=True)
except ImportError:
    print("Warning: Could not import logging config")

# Configure retry options
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)


def count_papers(papers: List[str]) -> int:
    """
    This function counts the number of papers in a list of strings.
    
    Args:
      papers: A list of strings, where each string is a research paper.
    Returns:
      The number of papers in the list.
    """
    return len(papers)


# Google Search agent
google_search_agent = LlmAgent(
    name="google_search_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Searches for information using Google search",
    instruction="""Use the google_search tool to find information on the given topic. Return the raw search results.
    If the user asks for a list of papers, then give them the list of research papers you found and not the summary.""",
    tools=[google_search],
)

print("✅ Google Search Agent created")

# Root agent - Research Paper Finder
research_agent = LlmAgent(
    name="research_paper_finder_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Your task is to find research papers and count them. 

    You MUST ALWAYS follow these steps:
    1) Find research papers on the user provided topic using the 'google_search_agent'. 
    2) Then, pass the papers to 'count_papers' tool to count the number of papers returned.
    3) Return both the list of research papers and the total number of papers.
    """,
    tools=[AgentTool(agent=google_search_agent), count_papers],
)

print("✅ Research Paper Finder Agent created")
print("   Tools: google_search_agent, count_papers")
print("   Ready for observability and debugging!")

# Define root_agent at module level for ADK web server compatibility
root_agent = research_agent

# Ensure logging is maintained after agent creation
try:
    ensure_debug_logging(agent_name="research_agent")
except NameError:
    pass

