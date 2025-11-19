# How to Set ADK_LOG_LEVEL=DEBUG

## Method 1: .env File (Recommended)

Create or edit a `.env` file in your agent's directory (e.g., `Day1b/ResearchAgent/.env`):

```bash
# Set log level to DEBUG
ADK_LOG_LEVEL=DEBUG
```

Or for INFO level:
```bash
ADK_LOG_LEVEL=INFO
```

## Method 2: Environment Variable (PowerShell)

```powershell
# Set for current session
$env:ADK_LOG_LEVEL = "DEBUG"

# Then run your agent
adk run .\ResearchAgent\
```

## Method 3: Environment Variable (Command Prompt)

```cmd
set ADK_LOG_LEVEL=DEBUG
adk run .\ResearchAgent\
```

## Method 4: In Code (Per-Agent Override)

```python
from utility.logging_config import setup_adk_logging

# Explicitly set to DEBUG
setup_adk_logging(agent_name="MyAgent", log_level="DEBUG", file_only=True)

# Or INFO
setup_adk_logging(agent_name="MyAgent", log_level="INFO", file_only=True)
```

## Method 5: Global .env File

Create a `.env` file in the root `5-day-agents` directory:

```bash
# This will apply to all agents that use the utility
ADK_LOG_LEVEL=DEBUG
```

## Available Log Levels

- `DEBUG` - Most verbose, includes all details
- `INFO` - Standard information (recommended for production)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors
- `CRITICAL` - Only critical errors

## Example .env File

```bash
# Logging Configuration
ADK_LOG_LEVEL=DEBUG

# Other environment variables
GOOGLE_API_KEY=your-api-key-here
GOOGLE_CLOUD_PROJECT=your-project-id
```

## Verification

After setting `ADK_LOG_LEVEL=DEBUG`, check your log file:

```powershell
# View the log file
Get-Content C:\Users\nares\AppData\Local\Temp\agents_log\agent.latest.log -Tail 20
```

You should see DEBUG level messages like:
```
2025-11-19 00:00:00 - google.genai._client - DEBUG - HTTP Request: POST ...
2025-11-19 00:00:00 - google.genai.google_llm - DEBUG - Sending out request...
```

## Quick Setup

1. **Create `.env` file** in your agent directory:
   ```bash
   ADK_LOG_LEVEL=DEBUG
   ```

2. **Your agent code** (already has this):
   ```python
   from utility.logging_config import setup_adk_logging
   setup_adk_logging(agent_name="MyAgent", file_only=True)
   ```

3. **That's it!** The agent will read `ADK_LOG_LEVEL` from `.env` automatically.

