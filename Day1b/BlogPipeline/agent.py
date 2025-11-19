from google.adk.agents import SequentialAgent
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for ADK using utility module
# Add project root to path to enable utility imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging - reads ADK_LOG_LEVEL from .env or defaults to DEBUG
setup_adk_logging(agent_name="BlogPipeline", file_only=True)

# Add Day1b directory to path to import sub-agents
day1b_dir = Path(__file__).parent.parent
sys.path.insert(0, str(day1b_dir))

from OutlineAgent.agent import outline_agent
from WriterAgent.agent import writer_agent
from EditorAgent.agent import editor_agent

root_agent = SequentialAgent(
    name="BlogPipeline",
    sub_agents=[outline_agent, writer_agent, editor_agent],
)

print("✅ Sequential Agent created.")


# Ensure logging is maintained after agent creation
ensure_debug_logging(agent_name="BlogPipeline")
