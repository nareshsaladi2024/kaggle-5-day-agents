# Using YAML Files for ADK Agent Discovery

## Overview

ADK web server can discover agents from YAML configuration files (`root_agent.yaml` or `agent.yaml`) instead of requiring Python `agent.py` files with `root_agent` variables.

## Quick Start

### 1. Create YAML Files

Run the helper script to auto-generate YAML files from existing agents:

```powershell
cd kaggle-5-day-agents
.\create-yaml-agents.ps1
```

This will create `root_agent.yaml` files in each agent subfolder.

### 2. Customize YAML Files

Edit the generated YAML files to customize agent configurations:

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

### 3. Run ADK Web Server

```powershell
# From kaggle-5-day-agents directory
adk web .
```

ADK will discover all agents with `root_agent.yaml` files.

## Directory Structure

```
kaggle-5-day-agents/
├── Day1a/
│   ├── root_agent.yaml          # Router agent for Day1a
│   ├── helpful_assistant/
│   │   ├── root_agent.yaml      # Individual agent
│   │   └── agent.py              # (optional, can use YAML instead)
│   └── sample-agent/
│       ├── root_agent.yaml       # Individual agent
│       └── agent.py
├── Day1b/
│   ├── ResearchAgent/
│   │   ├── root_agent.yaml
│   │   └── agent.py
│   └── ...
└── Day2b/
    └── ...
```

## YAML Configuration Options

### Basic Configuration

```yaml
name: agent_name
model:
  type: gemini
  model: gemini-2.5-flash-lite
description: Agent description
instruction: Agent instructions
```

### With Tools

```yaml
name: ResearchAgent
model:
  type: gemini
  model: gemini-2.5-flash-lite
description: Research agent
instruction: Research instructions
tools:
  - google_search
  - custom_tool
```

### With Retry Options

```yaml
name: helpful_assistant
model:
  type: gemini
  model: gemini-2.5-flash-lite
  retry_options:
    attempts: 5
    exp_base: 7
    initial_delay: 1
    http_status_codes: [429, 500, 503, 504]
description: Agent description
instruction: Agent instructions
tools:
  - google_search
```

### With Output Key

```yaml
name: ResearchAgent
model:
  type: gemini
  model: gemini-2.5-flash-lite
description: Research agent
instruction: Research instructions
tools:
  - google_search
output_key: research_findings
```

## Benefits of YAML Configuration

1. **Simpler Configuration**: No Python code needed for basic agents
2. **Easy Discovery**: ADK automatically finds YAML files
3. **Version Control Friendly**: YAML is easier to diff and review
4. **Flexible**: Can still use Python for complex agents
5. **Multiple Agents**: Each subfolder can have its own agent

## Mixing YAML and Python

You can use both:
- **YAML** for simple agent definitions
- **Python** for complex agents with custom logic

ADK will prefer YAML if both exist, or you can specify which to use.

## Troubleshooting

### Agent Not Found

1. Check that `root_agent.yaml` exists in the agent directory
2. Verify YAML syntax is correct (use a YAML validator)
3. Ensure the directory structure matches ADK expectations

### YAML Syntax Errors

Common issues:
- Missing colons after keys
- Incorrect indentation (use spaces, not tabs)
- Missing quotes for special characters

### Tools Not Working

Make sure tools are listed correctly:
```yaml
tools:
  - google_search  # Must match tool name exactly
```

## Examples

See:
- `Day1a/helpful_assistant/root_agent.yaml` - Simple agent
- `Day1a/sample-agent/root_agent.yaml` - Basic agent
- `Day1b/ResearchAgent/root_agent.yaml` - Agent with tools

## Next Steps

1. Run `.\create-yaml-agents.ps1` to generate YAML files
2. Customize the YAML files as needed
3. Run `adk web .` to start the web server
4. Access agents at http://localhost:8080

