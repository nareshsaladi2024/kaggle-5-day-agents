# Logging Quick Reference

## ✅ Do I Need to Add Logging to All Agents?

**Yes, but it's simple!** Just add 3 sections to each `agent.py`:

### 1. Add Imports (after other imports)
```python
import sys
from pathlib import Path
from utility.logging_config import setup_adk_logging, ensure_debug_logging
```

### 2. Setup Logging (before agent creation)
```python
# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Setup logging
setup_adk_logging(agent_name="YourAgentName", file_only=True)
```

### 3. Ensure Logging (after agent creation)
```python
# After: root_agent = Agent(...)
ensure_debug_logging(agent_name="YourAgentName")
```

## 🔧 How to Set ADK_LOG_LEVEL=DEBUG

### Option 1: .env File (Easiest)

Create/edit `.env` file in your agent directory:

```bash
ADK_LOG_LEVEL=DEBUG
```

### Option 2: PowerShell

```powershell
$env:ADK_LOG_LEVEL = "DEBUG"
```

### Option 3: In Code

```python
setup_adk_logging(agent_name="MyAgent", log_level="DEBUG", file_only=True)
```

## 📋 Complete Example

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Loads ADK_LOG_LEVEL from .env

# Add utility to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Setup logging (reads ADK_LOG_LEVEL from .env or defaults to DEBUG)
setup_adk_logging(agent_name="MyAgent", file_only=True)

# Create agent
root_agent = Agent(...)

# Ensure logging maintained
ensure_debug_logging(agent_name="MyAgent")
```

## 🎯 Summary

- ✅ **Add to all agents** - Use the template above
- ✅ **Set ADK_LOG_LEVEL=DEBUG** - Add to `.env` file
- ✅ **No code changes needed** - Just add the 3 sections
- ✅ **Works automatically** - Reads from `.env` file

## 📁 File Structure

```
5-day-agents/
├── utility/
│   └── logging_config.py  (reusable logging)
├── Day1b/
│   ├── ResearchAgent/
│   │   ├── agent.py       (add logging here)
│   │   └── .env           (add ADK_LOG_LEVEL=DEBUG here)
│   └── SummarizerAgent/
│       ├── agent.py       (add logging here)
│       └── .env           (add ADK_LOG_LEVEL=DEBUG here)
```

