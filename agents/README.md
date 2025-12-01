# Agents Directory

This directory contains all ADK agents in a flat structure for easy discovery.

## Usage

### View All Agents in Web UI

```powershell
# From agents/ directory
cd C:\Capstone\kaggle-5-day-agents\agents
adk web .
```

Or from parent directory:
```powershell
cd C:\Capstone\kaggle-5-day-agents
adk web agents
```

### Run a Specific Agent

```powershell
# Navigate to specific agent directory
cd C:\Capstone\kaggle-5-day-agents\agents\sample-agent
adk run .
```

### Use API Server (for ChatGPT)

```powershell
# From project root
cd C:\Capstone\kaggle-5-day-agents
python agents-api-server.py
```

## Available Agents

- helpful_assistant - General questions + weather
- sample-agent - Sample agent + weather
- currency_agent - Currency conversion
- image_agent - Image processing
- shipping_agent - Shipping workflows
- research_agent - Research and citations
- customer_support_agent - Customer support
- product_catalog_agent - Product catalog
- weather_assistant - Weather information
- Plus all Day1b research and writing agents

## Important Notes

- **`adk run .`** expects a SINGLE agent directory, not the agents/ container
- **`adk web .`** can discover MULTIPLE agents from a directory
- Each agent subdirectory must have `agent.py` with `root_agent` or `root_agent.yaml`

## Troubleshooting

### Error: "No root_agent found for 'agents'"

This happens when running `adk run .` from the `agents/` directory. 

**Solution**: Use `adk web .` instead, or navigate to a specific agent subdirectory.

### Error: "Agent not found"

Make sure:
1. Agent directory has `agent.py` with `root_agent` defined
2. Or has `root_agent.yaml` file
3. `.env` file exists if needed
4. All dependencies are installed
