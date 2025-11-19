# Quick Start: Logging in Agents

## One-Line Setup (Recommended)

Add this to the top of each agent file (after imports):

```python
from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging (reads ADK_LOG_LEVEL from .env or defaults to DEBUG)
setup_adk_logging(agent_name="YourAgentName", file_only=True)

# ... your agent code ...

# After agent creation
ensure_debug_logging(agent_name="YourAgentName")
```

## Three Ways to Control Log Level

### 1. Environment Variable (Best for all agents)
Add to `.env` file:
```bash
ADK_LOG_LEVEL=INFO    # or DEBUG, WARNING, ERROR
```

### 2. Per-Agent Override
```python
setup_adk_logging(agent_name="MyAgent", log_level="INFO", file_only=True)
```

### 3. After Agent Creation
```python
ensure_debug_logging(agent_name="MyAgent", log_level="INFO")
```

## Complete Example

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()

# Add utility to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# One line - reads ADK_LOG_LEVEL from .env or uses DEBUG
setup_adk_logging(agent_name="MyAgent", file_only=True)

# Create agent
root_agent = Agent(
    name="MyAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="You are helpful."
)

# Ensure logging maintained
ensure_debug_logging(agent_name="MyAgent")
```

**That's it!** No need to duplicate logging code - just import and call the function.

