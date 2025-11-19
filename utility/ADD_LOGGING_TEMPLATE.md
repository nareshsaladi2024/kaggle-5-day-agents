# Template: Adding Logging to Any Agent

## Quick Template

Add these lines to the top of your `agent.py` file (after imports, before agent creation):

```python
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (includes ADK_LOG_LEVEL)
load_dotenv()

# Add parent directory to path for utility imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging - reads ADK_LOG_LEVEL from .env or defaults to DEBUG
setup_adk_logging(agent_name="YourAgentName", file_only=True)
```

Then add this after your agent creation:

```python
# ... your agent code ...
root_agent = Agent(...)

# Ensure logging is maintained after agent creation
ensure_debug_logging(agent_name="YourAgentName")
```

## Complete Example

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add utility to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging (reads ADK_LOG_LEVEL from .env or defaults to DEBUG)
setup_adk_logging(agent_name="MyAgent", file_only=True)

# Create agent
retry_config = types.HttpRetryOptions(...)
root_agent = Agent(
    name="MyAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="You are helpful."
)

# Ensure logging maintained
ensure_debug_logging(agent_name="MyAgent")
```

## Where to Add

1. **After imports** - Add the utility imports
2. **Before agent creation** - Call `setup_adk_logging()`
3. **After agent creation** - Call `ensure_debug_logging()`

That's it! Just 3 additions to any agent file.

