# Day 5b: Deploy ADK Agent to Vertex AI Agent Engine

This directory contains a production-ready Weather Assistant agent and deployment scripts for Vertex AI Agent Engine.

## Overview

This tutorial demonstrates how to deploy ADK agents to production using [Vertex AI Agent Engine](https://docs.cloud.google.com/agent-builder/agent-engine/overview). You'll learn:

- How to build a production-ready ADK agent
- How to deploy your agent to Vertex AI Agent Engine using the ADK CLI
- How to test your deployed agent with Python SDK
- How to monitor and manage deployed agents
- How to clean up resources to avoid costs

## Architecture

```
┌─────────────────────────┐
│  Weather Assistant      │
│  Agent                  │
│  (Deployed to          │
│   Agent Engine)        │
└─────────────────────────┘
         │
         │ HTTP/Streaming
         │
┌─────────────────────────┐
│  Client Application     │
│  (Python SDK)          │
└─────────────────────────┘
```

## Directory Structure

```
Day5b/
├── WeatherAssistant/              # Agent code and configuration
│   ├── __init__.py
│   ├── agent.py                   # Weather Assistant agent
│   ├── requirements.txt           # Python dependencies
│   ├── .env.template              # Environment variables template
│   └── .agent_engine_config.json  # Agent Engine deployment config
├── deploy_to_agent_engine.py      # Deployment script
├── test_deployed_agent.py         # Test script for deployed agent
├── cleanup_agent.py               # Cleanup script
└── README.md                      # This file
```

## Prerequisites

### 1. Google Cloud Account Setup

- **Create a Google Cloud account** - [Sign up here](https://cloud.google.com/free)
  - New users get **$300 in free credits** valid for 90 days
- **Enable billing** - Required even for free trial
- **Create a project** - [Google Cloud Console](https://console.cloud.google.com/)

### 2. Enable Required APIs

Enable the following APIs in your Google Cloud project:

- Vertex AI API
- Cloud Storage API
- Cloud Logging API
- Cloud Monitoring API
- Cloud Trace API
- Telemetry API

[Enable APIs here](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com,storage.googleapis.com,logging.googleapis.com,monitoring.googleapis.com,cloudtrace.googleapis.com,telemetry.googleapis.com)

### 3. Install Dependencies

```bash
pip install google-adk
pip install opentelemetry-instrumentation-google-genai
```

### 4. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 5. Set Up Environment Variables

Copy the template and configure:

```bash
cd Day5b/WeatherAssistant
cp .env.template .env
```

Edit `.env` and set:
- `GOOGLE_CLOUD_PROJECT` - Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION` - Deployment region (e.g., "global", "us-east4")
- `GOOGLE_GENAI_USE_VERTEXAI=1` - Use Vertex AI backend

## Usage

### Step 1: Deploy the Agent

Deploy the Weather Assistant agent to Agent Engine:

```bash
cd Day5b
python deploy_to_agent_engine.py --project-id YOUR_PROJECT_ID --region us-east4
```

**Available regions:**
- `us-east4` (Virginia)
- `us-west1` (Oregon)
- `europe-west1` (Belgium)
- `europe-west4` (Netherlands)

**What happens:**
1. Packages your agent code
2. Uploads to Agent Engine
3. Creates a containerized deployment
4. Outputs a resource name

**Note:** Deployment typically takes 2-5 minutes.

### Step 2: Test the Deployed Agent

Once deployed, test your agent:

```bash
# Single query
python test_deployed_agent.py --project-id YOUR_PROJECT_ID --region us-east4 --query "What is the weather in Tokyo?"

# Run demo tests
python test_deployed_agent.py --project-id YOUR_PROJECT_ID --region us-east4 --demo
```

### Step 3: Clean Up (Important!)

**⚠️ Always delete resources when done testing to avoid costs!**

```bash
python cleanup_agent.py --project-id YOUR_PROJECT_ID --region us-east4
```

## Agent Configuration

### Deployment Settings (`.agent_engine_config.json`)

```json
{
    "min_instances": 0,
    "max_instances": 1,
    "resource_limits": {"cpu": "1", "memory": "1Gi"}
}
```

- `min_instances: 0` - Scales down to zero when not in use (saves costs)
- `max_instances: 1` - Maximum of 1 instance running
- `cpu: "1"` - 1 CPU core per instance
- `memory: "1Gi"` - 1 GB of memory per instance

### Environment Variables (`.env`)

- `GOOGLE_CLOUD_LOCATION="global"` - Uses the global endpoint for Gemini API calls
- `GOOGLE_GENAI_USE_VERTEXAI=1` - Configures ADK to use Vertex AI instead of Google AI Studio

## How It Works

### Weather Assistant Agent

The agent:
- Uses `gemini-2.5-flash-lite` for low latency and cost-efficiency
- Provides weather information for cities via `get_weather` tool
- Responds conversationally to user queries
- Demonstrates production deployment patterns

### Deployment Process

1. **Package** - ADK CLI packages your agent code and dependencies
2. **Upload** - Code is uploaded to Cloud Storage
3. **Build** - Agent Engine creates a containerized deployment
4. **Deploy** - Agent is deployed and ready to serve requests

### Testing the Deployed Agent

The test script:
1. Initializes Vertex AI SDK
2. Lists deployed agents
3. Connects to the most recent agent
4. Sends queries and streams responses

## Cost Management

### Free Tier

Agent Engine offers a monthly free tier. Learn more in the [documentation](https://docs.cloud.google.com/agent-builder/agent-engine/overview#pricing).

### Best Practices

1. **Delete test deployments** - Always clean up when done testing
2. **Use `min_instances: 0`** - Scales down to zero when not in use
3. **Monitor usage** - Check [Cloud Console](https://console.cloud.google.com/vertex-ai/agents/agent-engines) regularly
4. **Set up billing alerts** - Get notified of unexpected charges

## Monitoring

### View Deployed Agents

[Agent Engine Console](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

### View Logs

[Cloud Logging](https://console.cloud.google.com/logs)

### View Metrics

[Cloud Monitoring](https://console.cloud.google.com/monitoring)

## Troubleshooting

### Deployment Fails

- **Check authentication**: `gcloud auth login`
- **Verify project ID**: Ensure it's correct and billing is enabled
- **Check APIs**: Ensure all required APIs are enabled
- **Review permissions**: Ensure you have necessary IAM roles

### Agent Not Found

- **Wait 2-5 minutes**: Deployment takes time
- **Check region**: Ensure you're querying the correct region
- **List agents**: Use `agent_engines.list()` to see all agents

### Import Errors

- **Install dependencies**: `pip install google-adk`
- **Check Python version**: Requires Python 3.8+
- **Verify environment**: Ensure `.env` is configured correctly

## Advanced Topics

### Long-Term Memory with Memory Bank

Agent Engine supports [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank) for long-term memory across sessions.

**To enable Memory Bank:**
1. Add memory tools to your agent code (`PreloadMemoryTool`)
2. Add a callback to save conversations to Memory Bank
3. Redeploy your agent

**Learn more:**
- [ADK Memory Guide](https://google.github.io/adk-docs/sessions/memory/)
- [Memory Tools Documentation](https://google.github.io/adk-docs/tools/built-in-tools/)

### Other Deployment Options

- **Cloud Run** - Serverless, easiest to start
  - [Deploy to Cloud Run Guide](https://google.github.io/adk-docs/deploy/cloud-run/)
- **GKE** - Full control over containerized deployments
  - [Deploy to GKE Guide](https://google.github.io/adk-docs/deploy/gke/)

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Agent Engine Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [ADK Deployment Guide](https://google.github.io/adk-docs/deploy/agent-engine/)
- [Agent Engine Pricing](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#pricing)
- [Google Cloud Free Trial](https://cloud.google.com/free)

## Next Steps

1. **Customize the agent** - Add more tools and capabilities
2. **Integrate real APIs** - Replace mock weather data with real weather API
3. **Add memory** - Enable Memory Bank for long-term memory
4. **Monitor production** - Set up alerts and monitoring
5. **Scale up** - Adjust `max_instances` for production workloads

## Summary

You've learned how to:
- ✅ Build production-ready ADK agents
- ✅ Deploy to Vertex AI Agent Engine
- ✅ Test deployed agents
- ✅ Monitor and manage deployments
- ✅ Clean up resources to avoid costs

**Congratulations! You're ready for production deployment! 🚀**

