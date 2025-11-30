# Fix ADK Web Showing Folders Instead of Agents

## Problem
ADK web is showing "Day1a", "Day1b" folders instead of individual agents.

## Root Cause
ADK web was discovering agents hierarchically due to:
1. Root `root_agent.yaml` file (router agent)
2. Day-level `root_agent.yaml` files
3. Missing or incomplete `__init__.py` files

## Fixes Applied

### 1. Removed Root Router Agent
- Moved `root_agent.yaml` to `root_agent.yaml.backup`
- This was causing ADK to show a hierarchical router view

### 2. Removed Day-Level Config Files
- Removed `Day1a/root_agent.yaml` and similar files
- These were interfering with direct agent discovery

### 3. Removed Wrapper Files
- Removed all `agent_wrapper.py` files
- Agents are now discovered directly from subdirectories

### 4. Created Proper __init__.py Files
- Added `__init__.py` files in all agent directories
- Each file properly exposes `root_agent`:
  ```python
  from . import agent
  from .agent import root_agent
  __all__ = ['root_agent', 'agent']
  ```

## How to See Individual Agents

### Option 1: Restart ADK Web (Recommended)
```powershell
# Stop current ADK web (Ctrl+C)
# Then restart:
adk web . --no-reload
```

The `--no-reload` flag helps on Windows systems where auto-reload can cause issues.

### Option 2: Clear Cache and Restart
```powershell
# Stop ADK web
# Clear any cache
Remove-Item -Recurse -Force .adk -ErrorAction SilentlyContinue
# Restart
adk web .
```

### Option 3: Use Different Port
```powershell
adk web . --port 8081
```

## Expected Result

After restarting, ADK web should show a **flat list** of individual agents:

- helpful_assistant (with get_weather_for_city tool)
- sample-agent (with get_weather_in_london tool)
- currency_agent
- image_agent
- shipping_agent
- session_chat_bot
- memory_agent
- research_agent
- customer_support_agent
- product_catalog_agent
- weather_assistant
- And all Day1b agents (15+ agents)

**NOT** showing:
- ❌ Day1a (folder)
- ❌ Day1b (folder)
- ❌ Day2a (folder)

## Testing Weather Tools

Once agents are visible:

1. **Select `helpful_assistant`** and ask:
   - "What's the weather in London?"
   - "Get weather for New York"
   - "Tell me about Tokyo weather"

2. **Select `sample-agent`** and ask:
   - "What's the weather in London?"
   - "Get weather in London"

## Troubleshooting

### Still Seeing Folders?

1. **Verify no root_agent.yaml at root:**
   ```powershell
   Test-Path root_agent.yaml
   # Should return False
   ```

2. **Check for day-level root_agent.yaml:**
   ```powershell
   Get-ChildItem -Path . -Filter "root_agent.yaml" -Recurse | Where-Object { $_.Directory.Name -match "^Day\d+[ab]?$" }
   # Should return nothing
   ```

3. **Verify agent.py files have root_agent:**
   ```powershell
   Get-ChildItem -Path . -Filter "agent.py" -Recurse | Where-Object { (Get-Content $_.FullName -Raw) -match "root_agent\s*=" }
   # Should list all agent files
   ```

4. **Try running from a different directory:**
   ```powershell
   cd Day1a
   adk web .
   # Should show helpful_assistant and sample-agent directly
   ```

### Agents Not Loading?

1. Check for import errors in ADK web logs
2. Verify `.env` files exist in agent directories
3. Check Python path and dependencies
4. Try importing agents manually:
   ```python
   from Day1a.helpful_assistant.agent import root_agent
   ```

## Notes

- ADK web discovers agents recursively from the directory where you run `adk web`
- Agents must have `root_agent` defined at module level
- `__init__.py` files help Python discover modules properly
- Root-level router agents can cause hierarchical views

