# Kaggle 5-Day Agents

A comprehensive collection of AI agents built with Google ADK (Agent Development Kit), organized by learning days and deployed to Vertex AI Agent Engine and Cloud Run.

## Overview

This repository contains agents developed during a 5-day Kaggle course on building AI agents with Google ADK. The agents demonstrate various capabilities including research, content generation, customer support, weather assistance, and more.

## Repository Structure

```
kaggle-5-day-agents/
├── agents/              # Unified agents directory (for ADK web discovery)
├── Day1a/              # Basic agents: helpful_assistant, sample-agent
├── Day1b/              # Multi-agent pipelines: BlogPipeline, StoryPipeline
├── Day2a/              # Tools integration: CurrencyAgent
├── Day2b/              # Advanced tools: image_agent, shipping_agent
├── Day3a/              # Session management: session_agent, compaction_agent
├── Day3b/              # Memory systems: memory_agent, auto_memory_agent
├── Day4a/              # Observability: ResearchAgent with monitoring
├── Day4b/              # Agent evaluation: test suites and evaluation sets
├── Day5a/              # Agent-to-agent: CustomerSupportAgent, ProductCatalogAgent
├── Day5b/              # Deployment: WeatherAssistant with API server
└── utility/            # Shared utilities and helpers
```

## Key Features

- **30+ Production-Ready Agents**: From simple assistants to complex multi-agent pipelines
- **Multiple Deployment Options**: Cloud Run, Vertex AI Agent Engine, Docker Desktop
- **ChatGPT Integration**: FastAPI bridge for integrating agents with ChatGPT
- **ADK Web Discovery**: Unified agents directory for easy discovery and testing
- **Comprehensive Documentation**: Deployment guides, integration examples, troubleshooting

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud SDK (`gcloud`)
- Google ADK (`adk`)
- Docker (for containerized deployment)

### Local Development

```powershell
# Install dependencies
pip install -r requirements.txt

# Run ADK web UI to discover and test agents
adk web agents

# Run a specific agent
cd agents/sample-agent
adk run .
```

### Deploy to Vertex AI Agent Engine

```powershell
# Deploy all agents to Vertex AI Agent Engine
.\deploy-agents-to-agent-engine.ps1

# Deploy a specific agent
.\deploy-to-agent-engine.ps1 -AgentName "sample-agent"
```

### Deploy to Cloud Run

```powershell
# Deploy ADK web server to Cloud Run
.\deploy-to-cloud-run.ps1

# Deploy agents API server for ChatGPT integration
.\deploy-agents-api-to-cloud-run.ps1
```

### Deploy to Docker Desktop

```powershell
# Start ADK web server in Docker
.\docker-start.ps1
```

## Agent Categories

### Day 1: Basic Agents
- **helpful_assistant**: General-purpose assistant with weather tools
- **sample-agent**: Template agent for learning ADK basics

### Day 2: Tools Integration
- **CurrencyAgent**: Currency conversion with real-time exchange rates
- **image_agent**: Image processing and analysis
- **shipping_agent**: Shipping cost calculation and tracking

### Day 3: Sessions & Memory
- **session_agent**: Multi-turn conversation management
- **compaction_agent**: Session data compaction and optimization
- **memory_agent**: Persistent memory across conversations
- **auto_memory_agent**: Automatic memory management

### Day 4: Observability & Evaluation
- **ResearchAgent**: Web research with observability plugins
- **AgentEvaluation**: Comprehensive test suites and evaluation sets

### Day 5: Agent-to-Agent & Deployment
- **CustomerSupportAgent**: Customer service with product catalog integration
- **ProductCatalogAgent**: Product information and search
- **WeatherAssistant**: Weather information with API server deployment

### Multi-Agent Pipelines
- **BlogPipeline**: Multi-agent blog post generation
- **StoryPipeline**: Collaborative story writing
- **ParallelResearchTeam**: Parallel research coordination
- **ResearchCoordinator**: Research task orchestration

## Integration with ChatGPT

The repository includes a FastAPI bridge server (`agents-api-server.py`) that exposes ADK agents as REST endpoints for ChatGPT integration.

### Setup

1. Deploy the API server to Cloud Run:
   ```powershell
   .\deploy-agents-api-to-cloud-run.ps1
   ```

2. Configure ChatGPT Actions:
   - Use the OpenAPI schema (`openapi.yaml`)
   - Point to your deployed API server URL

See [CHATGPT_INTEGRATION.md](CHATGPT_INTEGRATION.md) for detailed instructions.

## Deployment Options

### Vertex AI Agent Engine
- **Best for**: Production agent deployment with Google Cloud integration
- **Features**: Auto-scaling, monitoring, managed infrastructure
- **Script**: `deploy-agents-to-agent-engine.ps1`

### Cloud Run
- **Best for**: API servers, web interfaces, containerized deployments
- **Features**: Serverless, pay-per-use, HTTP endpoints
- **Script**: `deploy-to-cloud-run.ps1`

### Docker Desktop
- **Best for**: Local development, testing, offline deployment
- **Features**: Full control, local execution
- **Script**: `docker-start.ps1`

See [CLOUD_RUN_VS_AGENT_ENGINE.md](CLOUD_RUN_VS_AGENT_ENGINE.md) for a detailed comparison.

## Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide
- [CHATGPT_INTEGRATION.md](CHATGPT_INTEGRATION.md) - ChatGPT integration instructions
- [INTEGRATE_VERTEX_AI_AGENTS.md](INTEGRATE_VERTEX_AI_AGENTS.md) - Vertex AI agent bridge
- [STOP_AGENTS_AGENT_ENGINE.md](STOP_AGENTS_AGENT_ENGINE.md) - Managing deployed agents
- [DOCKER_README.md](DOCKER_README.md) - Docker deployment guide

## Environment Setup

1. **Install Google ADK**:
   ```powershell
   pip install google-adk
   ```

2. **Authenticate with Google Cloud**:
   ```powershell
   gcloud auth application-default login
   ```

3. **Set Project ID**:
   ```powershell
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Enable Required APIs**:
   ```powershell
   gcloud services enable agentengine.googleapis.com
   gcloud services enable run.googleapis.com
   ```

## Managing Agents

### List Deployed Agents
```powershell
.\check-agent-engine-deployment.ps1
```

### Stop/Delete Agents
```powershell
.\stop-agents-in-agent-engine.ps1
```

### Sync Agents
```powershell
# Sync agents from Day folders to unified agents/ directory
.\sync-agents.ps1
```

## Contributing

This repository is part of a learning project. Agents are organized by learning day and demonstrate progressive complexity.

## License

MIT

## Repository

- **GitHub**: [kaggle-5-day-agents](https://github.com/nareshsaladi2024/kaggle-5-day-agents)
- **Technology Stack**: Google ADK, Vertex AI, Python, FastAPI, Docker
- **Deployment**: Vertex AI Agent Engine, Cloud Run, Docker Desktop

