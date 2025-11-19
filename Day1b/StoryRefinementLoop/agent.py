from google.adk.agents.llm_agent import Agent
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for ADK using utility module
# Add parent directory to path to enable utility imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging - reads ADK_LOG_LEVEL from .env or defaults to DEBUG
setup_adk_logging(agent_name="StoryRefinementLoop", file_only=True)
from CriticAgent.agent import critic_agent
from RefinerAgent.agent import refiner_agent
from InitialWriterAgent.agent import initial_writer_agent
from google.adk.agents import LoopAgent, SequentialAgent   
# The LoopAgent contains the agents that will run repeatedly: Critic -> Refiner.
story_refinement_loop = LoopAgent(
    name="StoryRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=2,  # Prevents infinite loops
)

# The root agent is a SequentialAgent that defines the overall workflow: Initial Write -> Refinement Loop.
root_agent = SequentialAgent(
    name="StoryPipeline",
    sub_agents=[initial_writer_agent, story_refinement_loop],
)

print("✅ Loop and Sequential Agents created.")

# Ensure logging is maintained after agent creation
ensure_debug_logging(agent_name="StoryRefinementLoop")
