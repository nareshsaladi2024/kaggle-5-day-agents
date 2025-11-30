# ADK Web Agent Discovery Fix

## Problem
ADK web was showing "Day1a", "Day1b", etc. as folders instead of showing individual agents.

## Solution
The wrapper `agent.py` files at the day level were interfering with ADK's recursive agent discovery. These files have been renamed to `agent_wrapper.py` to allow ADK web to discover agents directly from subdirectories.

## How ADK Web Discovers Agents

ADK web discovers agents by:
1. Recursively scanning directories for Python files with `root_agent` defined
2. Looking for `root_agent.yaml` or `agent.yaml` files
3. Starting from the directory where `adk web` is run (in this case, the root `.`)

## Current Agent Structure

All agents are now discoverable from their subdirectories:

### Day1a
- `Day1a/helpful_assistant/agent.py` → `helpful_assistant` agent
- `Day1a/sample-agent/agent.py` → `sample-agent` agent

### Day1b
- `Day1b/ResearchAgent/agent.py` → `research_agent`
- `Day1b/WriterAgent/agent.py` → `writer_agent`
- `Day1b/ResearchCoordinator/agent.py` → Research Coordinator
- And 12+ more agents...

### Day2a
- `Day2a/CurrencyAgent/agent.py` → `currency_agent`

### Day2b
- `Day2b/image_agent/agent.py` → `image_agent`
- `Day2b/shipping_agent/agent.py` → `shipping_agent`

### Day3a
- `Day3a/agents/session_agent.py` → `session_chat_bot`
- `Day3a/agents/basic_session_agent.py` → Basic Session Agent
- `Day3a/agents/compaction_agent.py` → Compaction Agent

### Day3b
- `Day3b/agents/memory_agent.py` → Memory Agent
- `Day3b/agents/auto_memory_agent.py` → Auto Memory Agent

### Day4a
- `Day4a/ResearchAgent/agent.py` → `research_agent`

### Day4b
- `Day4b/AgentEvaluation/home_automation_agent/agent.py` → Home Automation Agent

### Day5a
- `Day5a/CustomerSupportAgent/agent.py` → `customer_support_agent`
- `Day5a/ProductCatalogAgent/agent.py` → `product_catalog_agent`

### Day5b
- `Day5b/WeatherAssistant/agent.py` → Weather Assistant

## Testing

After rebuilding the Docker container, ADK web should now show all individual agents instead of day folders:

```bash
docker-compose up --build
```

Then access http://localhost:8080 and you should see all agents listed individually.

## Note

The `agent_wrapper.py` files are kept for reference but are not used by ADK web. They can be deleted if not needed, or kept for programmatic access to agents.

