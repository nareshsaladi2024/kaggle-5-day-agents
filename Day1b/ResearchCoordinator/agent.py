from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types
import vertexai
import os
import asyncio
from dotenv import load_dotenv
import sys
from pathlib import Path
import logging

# Load environment variables from .env file FIRST
# This allows environment variables to be available for logging configuration
load_dotenv()

# Configure detailed logging for ADK
# This enables DEBUG level logging to capture:
# - Events and traces
# - Request/Response details
# - Token usage information
# - Metadata and model interactions
# - HTTP request/response details
# 
# Note: We don't use force=True here because ADK sets up its own file handlers
# We'll configure logging after ADK initializes, or add our own file handler

# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Add a file handler to ensure logs go to file
# ADK creates log files in: %TEMP%\agents_log\agent.latest.log
log_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'agents_log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'agent.latest.log')

# Create a file handler with DEBUG level
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# Remove all StreamHandlers (stdout/stderr) - we only want file logging
for handler in root_logger.handlers[:]:
    if isinstance(handler, logging.StreamHandler):
        root_logger.removeHandler(handler)
    elif isinstance(handler, logging.FileHandler):
        # Remove any existing file handlers for the same file to avoid duplicates
        handler_path = getattr(handler, 'baseFilename', None) or getattr(getattr(handler, 'stream', None), 'name', None)
        if handler_path and log_file in str(handler_path):
            root_logger.removeHandler(handler)

# Add our file handler (only file handler, no stdout/stderr)
root_logger.addHandler(file_handler)

# Ensure file handler is set to DEBUG
file_handler.setLevel(logging.DEBUG)

# Set DEBUG level for ADK and related modules explicitly
logging.getLogger('adk').setLevel(logging.DEBUG)
logging.getLogger('google.adk').setLevel(logging.DEBUG)
logging.getLogger('google_adk').setLevel(logging.DEBUG)
logging.getLogger('google.genai').setLevel(logging.DEBUG)
logging.getLogger('google.genai.types').setLevel(logging.DEBUG)
logging.getLogger('google.genai._client').setLevel(logging.DEBUG)
logging.getLogger('google.genai.models').setLevel(logging.DEBUG)
logging.getLogger('google.genai.google_llm').setLevel(logging.DEBUG)

# Enable HTTP request/response logging (includes full request/response bodies)
logging.getLogger('httpx').setLevel(logging.DEBUG)
logging.getLogger('httpcore').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.DEBUG)

# Enable token and metadata logging
logging.getLogger('google.genai.google_llm').setLevel(logging.DEBUG)

# Log that debug logging is enabled
logging.debug("DEBUG logging enabled for ResearchCoordinator agent")

# Import the sub-agents from their respective modules
# Add parent directory to path to enable imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from ResearchAgent import research_agent
from SummarizerAgent import summarizer_agent

# Define root_agent at module level for ADK web server
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,  # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504]  # Retry on these HTTP errors
)

# Root Coordinator: Orchestrates the workflow by calling the sub-agents as tools.
root_agent = Agent(
    name="ResearchCoordinator",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    # This instruction tells the root agent HOW to use its tools (which are the other agents).
    instruction="""You are a research coordinator. Your goal is to answer the user's query by orchestrating a workflow.
1. First, you MUST call the `ResearchAgent` tool to find relevant information on the topic provided by the user.
2. Next, after receiving the research findings, you MUST call the `SummarizerAgent` tool to create a concise summary.
3. Finally, present the final summary clearly to the user as your response.""",
    # We wrap the sub-agents in `AgentTool` to make them callable tools for the root agent.
    tools=[AgentTool(research_agent), AgentTool(summarizer_agent)],
)

print("✅ root_agent created.")

# Ensure DEBUG logging is maintained after agent creation
# ADK might reset logging, so we re-apply DEBUG level
def ensure_debug_logging():
    """Ensure DEBUG logging is enabled for all relevant loggers and file handlers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Ensure log file handler exists and is configured for DEBUG
    log_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'agents_log')
    log_file = os.path.join(log_dir, 'agent.latest.log')
    
    # Remove all StreamHandlers (stdout/stderr) - we only want file logging
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            root_logger.removeHandler(handler)
        elif isinstance(handler, logging.FileHandler):
            # Remove any existing file handlers for the same file
            handler_path = getattr(handler, 'baseFilename', None) or getattr(getattr(handler, 'stream', None), 'name', None)
            if handler_path and log_file in str(handler_path):
                root_logger.removeHandler(handler)
    
    # Always add/ensure file handler exists (ADK might have removed it)
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set all relevant loggers to DEBUG
    loggers_to_debug = [
        'adk', 'google.adk', 'google_adk',
        'google.genai', 'google.genai.types', 'google.genai._client',
        'google.genai.models', 'google.genai.google_llm',
        'httpx', 'httpcore', 'urllib3'
    ]
    
    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        # Remove StreamHandlers from child loggers (only keep file handlers)
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                logger.removeHandler(handler)
            elif isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.DEBUG)
        # Propagate to root logger so file handler catches it
        logger.propagate = True
    
    # Also set root logger handlers to DEBUG (only file handlers should remain)
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.DEBUG)
        else:
            # Remove any non-file handlers that might have been added
            root_logger.removeHandler(handler)

# Call after agent creation to ensure logging stays at DEBUG
ensure_debug_logging()
logging.debug("DEBUG logging re-verified after agent creation")