# Cloud Deployment Logging Guide

## Overview

When deploying agents to **Vertex AI Reasoning Engine** or **Google Cloud Run**, the logging configuration automatically adapts to use Cloud Logging instead of file-based logging.

## How It Works

### Auto-Detection

The logging utility automatically detects cloud environments by checking for:
- `GOOGLE_CLOUD_PROJECT`
- `GCP_PROJECT`
- `CLOUD_RUN_SERVICE`
- `K_SERVICE` (Cloud Run service name)
- `VERTEX_AI_ENDPOINT`
- `GOOGLE_APPLICATION_CREDENTIALS`

### Logging Behavior

| Environment | Log Destination | Handler Type |
|------------|----------------|--------------|
| **Local** | File (`%TEMP%\agents_log\agent.latest.log`) | FileHandler |
| **Cloud** | stdout/stderr → Cloud Logging | StreamHandler |

## Configuration

### Option 1: Auto-Detection (Recommended)

No code changes needed! The utility automatically detects the environment:

```python
from utility.logging_config import setup_adk_logging, ensure_debug_logging

# Automatically uses file logging locally, stdout/stderr in cloud
setup_adk_logging(agent_name="MyAgent")
# ... agent code ...
ensure_debug_logging(agent_name="MyAgent")
```

### Option 2: Explicit Cloud Mode

If auto-detection doesn't work, explicitly set cloud mode:

```python
# For cloud deployment
setup_adk_logging(agent_name="MyAgent", cloud_mode=True)

# For local development
setup_adk_logging(agent_name="MyAgent", cloud_mode=False)
```

### Option 3: Environment Variable

Set `ADK_CLOUD_MODE` to force cloud mode:

```bash
# In your deployment environment or .env file
ADK_CLOUD_MODE=TRUE
```

## Log Levels in Cloud

Set log level via environment variable (works in both local and cloud):

```bash
# In Cloud Run or Vertex AI environment variables
ADK_LOG_LEVEL=INFO    # or DEBUG, WARNING, ERROR
```

Or in your agent code:

```python
setup_adk_logging(agent_name="MyAgent", log_level="INFO", cloud_mode=True)
```

## Viewing Logs in Cloud

### Cloud Run

1. **Google Cloud Console:**
   - Navigate to Cloud Run → Your Service → Logs
   - Or use: `gcloud run services logs read <service-name>`

2. **Cloud Logging:**
   - Go to Cloud Logging in GCP Console
   - Filter by: `resource.type="cloud_run_revision"`

### Vertex AI Reasoning Engine

1. **Google Cloud Console:**
   - Navigate to Vertex AI → Reasoning Engine → Your Agent → Logs

2. **Cloud Logging:**
   - Filter by: `resource.type="aiplatform.googleapis.com/Endpoint"`

## Best Practices

### 1. Use INFO Level in Production

```python
# Production deployment
setup_adk_logging(agent_name="MyAgent", log_level="INFO", cloud_mode=True)
```

### 2. Use DEBUG Level for Development

```python
# Local development
setup_adk_logging(agent_name="MyAgent", log_level="DEBUG", file_only=True)
```

### 3. Set via Environment Variables

In your Cloud Run or Vertex AI deployment configuration:

```bash
ADK_LOG_LEVEL=INFO
ADK_CLOUD_MODE=TRUE  # Optional, auto-detected if not set
```

## Example: Complete Cloud Deployment

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

# Auto-detects cloud environment and uses stdout/stderr for Cloud Logging
setup_adk_logging(agent_name="MyAgent")

# Create agent
root_agent = Agent(
    name="MyAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="You are helpful."
)

# Ensure logging maintained
ensure_debug_logging(agent_name="MyAgent")
```

## Troubleshooting

### Logs Not Appearing in Cloud Logging

1. **Check environment variables:**
   ```bash
   echo $ADK_CLOUD_MODE
   echo $ADK_LOG_LEVEL
   ```

2. **Verify auto-detection:**
   - Check if cloud environment variables are set
   - Or explicitly set `cloud_mode=True`

3. **Check log level:**
   - Ensure `ADK_LOG_LEVEL` is set appropriately
   - DEBUG logs won't appear if level is set to INFO

### Too Many Logs in Production

Set log level to INFO or WARNING:

```bash
ADK_LOG_LEVEL=INFO
```

## Summary

✅ **No code changes needed** - auto-detects cloud vs local  
✅ **Logs automatically go to Cloud Logging** in cloud environments  
✅ **Same code works** in both local and cloud  
✅ **Configurable log levels** via environment variables  
✅ **View logs** in Google Cloud Console → Cloud Logging

