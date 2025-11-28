# ADK Agent Configuration with YAML Files

This guide explains how to define agents using `root_agent.yaml` or `agent.yaml` files for ADK web server discovery.

## Directory Structure

ADK web server expects one of these structures:

```
<agents_dir>/
  <agent_name>/
    agent.py (with root_agent) OR
    root_agent.yaml
```

## YAML Configuration Format

### Basic Agent YAML

Create a `root_agent.yaml` file in each agent directory:

```yaml
name: helpful_assistant
model:
  type: gemini
  model: gemini-2.5-flash-lite
description: A simple agent that can answer general questions.
instruction: You are a helpful assistant. Use Google Search for current info or if unsure.
tools:
  - google_search
```

### Advanced Agent YAML

```yaml
name: ResearchAgent
model:
  type: gemini
  model: gemini-2.5-flash-lite
  retry_options:
    attempts: 5
    exp_base: 7
    initial_delay: 1
    http_status_codes: [429, 500, 503, 504]
description: A specialized research agent that finds relevant information.
instruction: |
  You are a specialized research agent. Your only job is to use the
  google_search tool to find 2-3 pieces of relevant information on the given topic 
  and present the findings with citations.
tools:
  - google_search
output_key: research_findings
```

## Creating YAML Files for Your Agents

### Option 1: Create root_agent.yaml in Each Subfolder

For each agent subfolder (e.g., `Day1a/helpful_assistant/`), create a `root_agent.yaml`:

```yaml
# Day1a/helpful_assistant/root_agent.yaml
name: helpful_assistant
model:
  type: gemini
  model: gemini-2.5-flash-lite
description: A simple agent that can answer general questions.
instruction: You are a helpful assistant. Use Google Search for current info or if unsure.
tools:
  - google_search
```

### Option 2: Create root_agent.yaml at Day Level

For each Day folder (e.g., `Day1a/`), create a `root_agent.yaml` that references sub-agents:

```yaml
# Day1a/root_agent.yaml
name: Day1a
model:
  type: gemini
  model: gemini-2.5-flash-lite
description: Day1a agent collection
instruction: |
  You are a router agent for Day1a. You can access:
  - helpful_assistant: A simple assistant
  - sample-agent: A sample agent
```

### Option 3: Use Python with YAML Import

You can also use Python to load from YAML:

```python
# agent.py
import yaml
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

# Load config from YAML
with open('root_agent.yaml', 'r') as f:
    config = yaml.safe_load(f)

root_agent = Agent(
    name=config['name'],
    model=Gemini(model=config['model']['model']),
    description=config['description'],
    instruction=config['instruction'],
    tools=[google_search] if 'google_search' in config.get('tools', []) else []
)
```

## Running ADK Web Server

Once you have YAML files set up:

```powershell
# From Capstone directory
cd kaggle-5-day-agents
adk web .

# Or from specific Day folder
cd Day1a
adk web .
```

## Examples

See the `examples/` directory for complete YAML configurations for:
- Simple agents
- Agents with tools
- Sequential agents
- Parallel agents
- Complex workflows

