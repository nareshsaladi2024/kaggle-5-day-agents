# Utility Module

This module contains reusable utility functions for ADK agents.

## Logging Configuration

The `logging_config` module provides functions to configure detailed DEBUG-level logging for ADK agents.

### Usage

#### Basic Usage (Uses DEBUG by default or ADK_LOG_LEVEL env var)

```python
from utility.logging_config import setup_adk_logging

# Setup logging at the beginning of your agent file
# Uses DEBUG level by default, or reads from ADK_LOG_LEVEL environment variable
setup_adk_logging(agent_name="MyAgent", file_only=True)
```

#### Configure Log Level

You can set the log level in three ways:

**1. Environment Variable (Recommended for all agents)**
```bash
# Set in your .env file or environment
ADK_LOG_LEVEL=INFO
# or
ADK_LOG_LEVEL=DEBUG
```

**2. Function Parameter (Per-agent override)**
```python
from utility.logging_config import setup_adk_logging

# Set to INFO level
setup_adk_logging(agent_name="MyAgent", log_level="INFO", file_only=True)

# Or use logging constants
import logging
setup_adk_logging(agent_name="MyAgent", log_level=logging.INFO, file_only=True)
```

**3. After Agent Creation**
```python
from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging (uses env var or default)
setup_adk_logging(agent_name="MyAgent", file_only=True)

# Create your agent
root_agent = Agent(...)

# Ensure logging is maintained (can override level here too)
ensure_debug_logging(agent_name="MyAgent", log_level="INFO")
```

### Function Parameters

#### `setup_adk_logging()`

- `agent_name` (Optional[str]): Name of the agent for logging identification
- `log_file` (Optional[str]): Path to log file. If None, uses ADK's default location (`%TEMP%\agents_log\agent.latest.log`)
- `log_level` (Union[str, int, None]): Logging level as string ("DEBUG", "INFO", "WARNING", "ERROR") or int (logging.DEBUG, etc.)
  - If None, reads from `ADK_LOG_LEVEL` environment variable
  - If env var not set, defaults to `DEBUG`
- `file_only` (bool): If True, removes stdout/stderr handlers (default: True)

#### `ensure_debug_logging()`

- `agent_name` (Optional[str]): Name of the agent for logging identification
- `log_level` (Union[str, int, None]): Optional log level override. If None, uses same logic as `setup_adk_logging`

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
from dotenv import load_dotenv

# Load environment variables (includes ADK_LOG_LEVEL if set)
load_dotenv()

# Add parent directory to path for utility imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging (reads ADK_LOG_LEVEL from .env or defaults to DEBUG)
setup_adk_logging(agent_name="MyAgent", file_only=True)

# Create agent
root_agent = Agent(
    name="MyAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="You are a helpful assistant."
)

# Ensure logging is maintained (uses same level as setup)
ensure_debug_logging(agent_name="MyAgent")
```

### Example: Per-Agent Log Level Override

```python
# Production agent with INFO level
setup_adk_logging(agent_name="ProductionAgent", log_level="INFO", file_only=True)

# Development agent with DEBUG level
setup_adk_logging(agent_name="DevAgent", log_level="DEBUG", file_only=True)
```

### Environment Variable Configuration

Add to your `.env` file to set log level for all agents:

```bash
# Set to INFO for production, DEBUG for development
ADK_LOG_LEVEL=INFO
# or
ADK_LOG_LEVEL=DEBUG
```

This way, you don't need to modify each agent file - just set the environment variable!

