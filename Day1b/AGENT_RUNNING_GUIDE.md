# Agent Running Guide

## Running Agents Standalone vs. as Sub-Agents

In this project, agents can be used in two ways:

### 1. Standalone (Root Agent)

You can run any agent individually using ADK:

```powershell
# Run ResearchAgent standalone
adk run .\ResearchAgent\

# Run SummarizerAgent standalone
adk run .\SummarizerAgent\

# Run ResearchCoordinator (the main orchestrator)
adk run .\ResearchCoordinator\
```

### 2. As Sub-Agents

Agents can also be used as tools by other agents. For example:
- `ResearchAgent` and `SummarizerAgent` are used as tools by `ResearchCoordinator`
- They are imported and wrapped in `AgentTool` to be callable

## How It Works

Each agent file exposes the agent in two ways:

1. **Named variable** (e.g., `research_agent`, `summarizer_agent`): Used when importing as a sub-agent
2. **`root_agent`**: Required by ADK when running standalone

Example from `ResearchAgent/agent.py`:

```python
# Create the agent
research_agent = Agent(
    name="ResearchAgent",
    ...
)

# Expose as root_agent for ADK to find when running standalone
root_agent = research_agent
```

This pattern allows the same agent to be:
- ✅ Run standalone: `adk run .\ResearchAgent\`
- ✅ Used as a sub-agent: Imported by `ResearchCoordinator` as `research_agent`

## Agent Hierarchy

```
ResearchCoordinator (Root Orchestrator)
├── ResearchAgent (can run standalone)
└── SummarizerAgent (can run standalone)
```

- **ResearchCoordinator**: The main agent that orchestrates the workflow
- **ResearchAgent**: Can run standalone OR be used by ResearchCoordinator
- **SummarizerAgent**: Can run standalone OR be used by ResearchCoordinator

## Running Individual Agents

To test or use individual agents:

```powershell
# Test ResearchAgent alone
cd Day1b
adk run .\ResearchAgent\

# Test SummarizerAgent alone
adk run .\SummarizerAgent\

# Run the full workflow
adk run .\ResearchCoordinator\
```

Each agent will work independently, but `ResearchCoordinator` orchestrates them together for a complete workflow.

