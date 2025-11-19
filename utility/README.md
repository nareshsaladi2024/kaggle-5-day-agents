# Utility Module

This module contains reusable utility functions for ADK agents.

## Logging Configuration

The `logging_config` module provides functions to configure detailed DEBUG-level logging for ADK agents.

### Usage

#### Basic Usage

```python
from utility.logging_config import setup_adk_logging

# Setup logging at the beginning of your agent file
setup_adk_logging(agent_name="MyAgent", file_only=True)
```

#### After Agent Creation

```python
from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging
setup_adk_logging(agent_name="MyAgent", file_only=True)

# Create your agent
root_agent = Agent(...)

# Ensure logging is maintained after agent creation
ensure_debug_logging(agent_name="MyAgent")
```

### Function Parameters

#### `setup_adk_logging()`

- `agent_name` (Optional[str]): Name of the agent for logging identification
- `log_file` (Optional[str]): Path to log file. If None, uses ADK's default location (`%TEMP%\agents_log\agent.latest.log`)
- `log_level` (int): Logging level (default: `logging.DEBUG`)
- `file_only` (bool): If True, removes stdout/stderr handlers (default: True)

#### `ensure_debug_logging()`

- `agent_name` (Optional[str]): Name of the agent for logging identification

### What Gets Logged

When using `setup_adk_logging()`, the following information is captured:

- **Events and traces**: All ADK internal events and execution traces
- **Request/Response details**: Full HTTP request and response bodies
- **Token usage**: Token counts (input/output) in response metadata
- **Metadata**: Model configuration, retry attempts, and other metadata
- **Model interactions**: Detailed information about each LLM call

### Log File Location

By default, logs are written to:
- Windows: `%TEMP%\agents_log\agent.latest.log`
- Unix/Linux: `~/agents_log/agent.latest.log`

You can specify a custom location using the `log_file` parameter.

### Example: Complete Agent Setup

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
from pathlib import Path
import sys

# Add parent directory to path for utility imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging
setup_adk_logging(agent_name="MyAgent", file_only=True)

# Create agent
root_agent = Agent(
    name="MyAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="You are a helpful assistant."
)

# Ensure logging is maintained
ensure_debug_logging(agent_name="MyAgent")
```

