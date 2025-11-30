# Day 5a: Agent2Agent (A2A) Communication

This directory contains agents that demonstrate **Agent2Agent (A2A) Protocol** communication using ADK.

## Overview

This tutorial demonstrates how to build multi-agent systems where different agents communicate and collaborate using the A2A Protocol. You'll learn:

- How to expose an ADK agent via A2A using `to_a2a()`
- How to consume remote agents using `RemoteA2aAgent`
- How agents can communicate across networks, frameworks, and organizations

## Architecture

```
┌──────────────────────┐           ┌──────────────────────┐
│ Customer Support     │  ─A2A──▶  │ Product Catalog      │
│ Agent (Consumer)     │           │ Agent (Vendor)       │
│ Your Company         │           │ External Service     │
│ (localhost:8000)     │           │ (localhost:8001)     │
└──────────────────────┘           └──────────────────────┘
```

## Directory Structure

```
Day5a/
├── ProductCatalogAgent/      # External vendor agent (exposed via A2A)
│   ├── __init__.py
│   └── agent.py
├── CustomerSupportAgent/      # Consumer agent (uses Product Catalog via A2A)
│   ├── __init__.py
│   └── agent.py
├── run_product_catalog_server.py  # Script to start Product Catalog server
├── run_a2a_demo.py            # Demo script to test A2A communication
└── README.md                  # This file
```

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install google-adk[a2a]
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root with:
   ```
   GOOGLE_API_KEY=your_api_key_here
   PRODUCT_CATALOG_PORT=8001
   PRODUCT_CATALOG_URL=http://localhost:8001
   ```

## Usage

### Step 1: Start the Product Catalog Agent Server

In one terminal, start the Product Catalog Agent server:

```bash
cd Day5a
python run_product_catalog_server.py
```

The server will start on `http://localhost:8001` (or the port specified in `PRODUCT_CATALOG_PORT`).

You should see:
```
✅ Product Catalog Agent created successfully!
✅ Product Catalog Agent is now A2A-compatible!
   Agent will be served at: http://localhost:8001
   Agent card will be at: http://localhost:8001/.well-known/agent-card.json
```

### Step 2: Test A2A Communication

In another terminal, run the demo script:

```bash
cd Day5a
python run_a2a_demo.py
```

This will test the A2A communication between the Customer Support Agent and Product Catalog Agent.

## How It Works

### Product Catalog Agent

The `ProductCatalogAgent` is an external vendor's agent that:
- Provides product information from a catalog
- Is exposed via A2A protocol using `to_a2a()`
- Auto-generates an agent card at `/.well-known/agent-card.json`
- Runs as a separate service (simulating external vendor infrastructure)

### Customer Support Agent

The `CustomerSupportAgent` is your internal agent that:
- Helps customers with product inquiries
- Uses `RemoteA2aAgent` to connect to the Product Catalog Agent
- Communicates with Product Catalog Agent via A2A protocol
- Doesn't need to know the Product Catalog Agent is remote

### A2A Communication Flow

1. Customer asks Support Agent a question about a product
2. Support Agent realizes it needs product info
3. Support Agent calls the `remote_product_catalog_agent` (RemoteA2aAgent)
4. ADK sends an A2A protocol request to `http://localhost:8001`
5. Product Catalog Agent processes the request and responds
6. Support Agent receives the response and continues
7. Customer gets the final answer

## Key Concepts

### A2A Protocol

The [Agent2Agent (A2A) Protocol](https://a2a-protocol.org/) is a standard that allows agents to:
- Communicate over networks (agents can be on different machines)
- Use each other's capabilities (one agent can call another like a tool)
- Work across frameworks (language/framework agnostic)
- Maintain formal contracts (agent cards describe capabilities)

### Agent Cards

An **agent card** is a JSON document that serves as a "business card" for your agent. It describes:
- What the agent does (name, description, version)
- What capabilities it has (skills, tools, functions)
- How to communicate with it (URL, protocol version, endpoints)

Every A2A agent must publish its agent card at: `/.well-known/agent-card.json`

### When to Use A2A vs Local Sub-Agents

| Factor | Use A2A | Use Local Sub-Agents |
|--------|---------|---------------------|
| **Agent Location** | External service, different codebase | Same codebase, internal |
| **Ownership** | Different team/organization | Your team |
| **Network** | Agents on different machines | Same process/machine |
| **Performance** | Network latency acceptable | Need low latency |
| **Language/Framework** | Cross-language/framework needed | Same language |
| **Contract** | Formal API contract required | Internal interface |

## Viewing the Agent Card

You can view the auto-generated agent card by visiting:
```
http://localhost:8001/.well-known/agent-card.json
```

This shows the Product Catalog Agent's capabilities and how to communicate with it.

## Troubleshooting

### Server not starting
- Make sure port 8001 (or your configured port) is not in use
- Check that `GOOGLE_API_KEY` is set in your `.env` file

### Connection errors
- Ensure the Product Catalog Agent server is running before running the demo
- Verify `PRODUCT_CATALOG_URL` matches the server URL
- Check firewall settings if running on different machines

### Import errors
- Make sure you're running from the correct directory
- Verify that `google-adk[a2a]` is installed: `pip install google-adk[a2a]`

## Next Steps

1. **Add More Agents**: Create additional agents (Inventory, Shipping) and have them communicate via A2A
2. **Real Data Sources**: Replace mock product catalog with real database
3. **Deploy to Production**: Deploy agents to Cloud Run or Agent Engine
4. **Authentication**: Add API keys or OAuth for secure agent communication

## Resources

- [A2A Protocol Official Website](https://a2a-protocol.org/)
- [A2A Protocol Specification](https://a2a-protocol.org/latest/spec/)
- [ADK A2A Documentation](https://google.github.io/adk-docs/a2a/intro/)
- [Exposing Agents Quickstart](https://google.github.io/adk-docs/a2a/quickstart-exposing/)
- [Consuming Agents Quickstart](https://google.github.io/adk-docs/a2a/quickstart-consuming/)

