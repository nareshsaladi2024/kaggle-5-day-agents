# Day 2a: Agent Tools

This directory contains agents that demonstrate custom function tools and agent tools using ADK.

## Overview

This tutorial demonstrates how to build agents with custom tools. You'll learn:

- How to convert Python functions into agent tools
- How to use other agents as tools (Agent Tools)
- How to use code execution for reliable calculations
- Best practices for building custom tools

## Directory Structure

```
Day2a/
├── CurrencyAgent/              # Currency converter agent
│   ├── __init__.py
│   └── agent.py                # Agent with custom function tools and agent tools
├── run_currency_agent.py       # Demo script
└── README.md                   # This file
```

## Key Concepts

### Custom Function Tools

Any Python function can become an agent tool by:
1. Creating a Python function with clear docstrings
2. Using type hints for parameters
3. Returning structured dictionaries with status
4. Adding the function to the agent's `tools=[]` list

**Example:**
```python
def get_fee_for_payment_method(method: str) -> dict:
    """Looks up transaction fee for a payment method."""
    # ... implementation
    return {"status": "success", "fee_percentage": 0.02}
```

### Agent Tools

You can use other agents as tools using `AgentTool`:

```python
from google.adk.tools import AgentTool

enhanced_agent = LlmAgent(
    tools=[
        get_fee_for_payment_method,
        get_exchange_rate,
        AgentTool(agent=calculation_agent),  # Another agent as a tool!
    ]
)
```

**Agent Tools vs Sub-Agents:**
- **Agent Tools**: Agent A calls Agent B as a tool, Agent A stays in control
- **Sub-Agents**: Agent A transfers control completely to Agent B

### Code Execution

For reliable calculations, use `BuiltInCodeExecutor`:

```python
from google.adk.code_executors import BuiltInCodeExecutor

calculation_agent = LlmAgent(
    code_executor=BuiltInCodeExecutor(),  # Enables code execution
    instruction="Generate Python code for calculations..."
)
```

## Usage

### Run the Demo

```bash
cd Day2a
python run_currency_agent.py
```

This will:
1. Test the basic currency agent with function tools
2. Test the enhanced currency agent with agent tools and code execution

## Agent Architecture

### Basic Currency Agent

```
Currency Agent
├── get_fee_for_payment_method()  # Function tool
└── get_exchange_rate()            # Function tool
```

### Enhanced Currency Agent

```
Enhanced Currency Agent
├── get_fee_for_payment_method()   # Function tool
├── get_exchange_rate()            # Function tool
└── calculation_agent              # Agent tool
    └── BuiltInCodeExecutor        # Code execution
```

## Tool Best Practices

1. **Dictionary Returns**: Return `{"status": "success", "data": ...}` or `{"status": "error", "error_message": ...}`
2. **Clear Docstrings**: LLMs use docstrings to understand when and how to use tools
3. **Type Hints**: Enable ADK to generate proper schemas
4. **Error Handling**: Structured error responses help LLMs handle failures gracefully

## Available Tools

### Function Tools
- `get_fee_for_payment_method(method: str)` - Looks up transaction fees
- `get_exchange_rate(base_currency: str, target_currency: str)` - Gets exchange rates

### Agent Tools
- `calculation_agent` - Specialist agent for reliable calculations using code execution

## Example Queries

- "I want to convert 500 US Dollars to Euros using my Platinum Credit Card. How much will I receive?"
- "Convert 1,250 USD to INR using a Bank Transfer. Show me the precise calculation."

## Resources

- [ADK Tools Documentation](https://google.github.io/adk-docs/tools/)
- [ADK Custom Tools Guide](https://google.github.io/adk-docs/tools-custom/)
- [ADK Function Tools](https://google.github.io/adk-docs/tools/function-tools/)
- [ADK Plugins Overview](https://google.github.io/adk-docs/plugins/)

## Next Steps

- Explore more tool types (MCP Tools, OpenAPI Tools)
- Learn about long-running function tools
- Build multi-agent systems with specialized agents

