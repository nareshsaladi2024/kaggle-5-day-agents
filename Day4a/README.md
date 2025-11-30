# Day 4a: Agent Observability

This directory contains agents that demonstrate observability, debugging, and logging in ADK.

## Overview

This tutorial demonstrates how to add observability to your agents. You'll learn:

- How to debug agent failures using logs and traces
- How to use ADK Web UI for interactive debugging
- How to implement logging for production systems
- How to use LoggingPlugin and create custom plugins

## Directory Structure

```
Day4a/
├── ResearchAgent/                    # Research paper finder agent
│   ├── __init__.py
│   └── agent.py                     # Agent with observability
├── run_research_agent.py            # Demo script with LoggingPlugin
├── observability_plugin_example.py  # Custom plugin example
└── README.md                        # This file
```

## Key Concepts

### Observability Pillars

1. **Logs**: Records of single events - what happened at a specific moment
2. **Traces**: Connected logs showing the complete sequence of steps - why a result occurred
3. **Metrics**: Summary numbers (averages, error rates) - how well the agent performs

### Debugging with ADK Web UI

Use `adk web --log_level DEBUG` to:
- See full LLM prompts and responses
- View detailed API responses
- Inspect internal state transitions
- Debug agent failures interactively

```bash
adk web --log_level DEBUG
```

### LoggingPlugin

ADK's built-in `LoggingPlugin` automatically captures:
- 🚀 User messages and agent responses
- ⏱️ Timing data for performance analysis
- 🧠 LLM requests and responses
- 🔧 Tool calls and results
- ✅ Complete execution traces

```python
from google.adk.plugins.logging_plugin import LoggingPlugin

runner = InMemoryRunner(
    agent=my_agent,
    plugins=[LoggingPlugin()]
)
```

### Custom Plugins

Create custom plugins for specific observability needs:

```python
from google.adk.plugins.base_plugin import BasePlugin

class MyCustomPlugin(BasePlugin):
    async def before_agent_callback(self, *, agent, callback_context):
        # Your custom logging logic
        pass
```

## Usage

### Run with Observability

```bash
cd Day4a
python run_research_agent.py
```

This demonstrates:
- LoggingPlugin for comprehensive observability
- Agent execution traces
- Tool calls and responses

### Debug with ADK Web UI

1. Start the ADK web UI:
   ```bash
   adk web --log_level DEBUG
   ```

2. Open the web interface (typically `http://localhost:8000`)

3. Select your agent and test queries

4. View logs, traces, and events in the UI

### Custom Plugin Example

See `observability_plugin_example.py` for a complete example of a custom plugin that tracks:
- Agent invocation counts
- Tool call counts
- LLM request counts

## Agent Architecture

```
Research Paper Finder Agent
├── google_search_agent          # Sub-agent for searching
│   └── google_search tool
└── count_papers                  # Function tool
```

## When to Use Which Logging?

1. **Development debugging?** → Use `adk web --log_level DEBUG`
2. **Common production observability?** → Use `LoggingPlugin()`
3. **Custom requirements?** → Build Custom Callbacks and Plugins

## Debugging Pattern

**Core debugging pattern:** `symptom → logs → root cause → fix`

1. **Symptom**: Agent fails or behaves unexpectedly
2. **Logs**: Check logs and traces to see what happened
3. **Root Cause**: Identify the exact failure point
4. **Fix**: Apply the appropriate solution

## Example Debugging Scenarios

### Missing Tools
```
Symptom: Agent says "I cannot help with that request"
Logs: LLM Request shows "Functions: []" (no tools!)
Fix: Add missing tools to agent
```

### Type Mismatch
```
Symptom: Tool returns unexpected result
Logs: Function call shows wrong parameter type
Fix: Correct function signature and type hints
```

### Performance Issues
```
Symptom: Agent is slow
Traces: Identify which step takes longest
Fix: Optimize slow operations or add caching
```

## Plugin Callbacks

Available callbacks for custom plugins:

- `before_agent_callback` - Runs before an agent is invoked
- `after_agent_callback` - Runs after an agent completes
- `before_tool_callback` - Runs before a tool is called
- `after_tool_callback` - Runs after a tool completes
- `before_model_callback` - Runs before LLM model is called
- `after_model_callback` - Runs after LLM model responds
- `on_model_error_callback` - Runs when a model error occurs

## Resources

- [ADK Observability Documentation](https://google.github.io/adk-docs/observability/logging/)
- [Custom Plugin Guide](https://google.github.io/adk-docs/plugins/)
- [External Integrations](https://google.github.io/adk-docs/observability/cloud-trace/)
- [ADK Web UI](https://google.github.io/adk-docs/cli/web/)

## Next Steps

- Explore external observability integrations (Cloud Trace, etc.)
- Build custom plugins for specific monitoring needs
- Learn about agent evaluation (Day 4b)

