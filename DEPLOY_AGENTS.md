# Deploy Agents to Cloud Run and Vertex AI Agent Engine

This guide shows how to deploy agents from the `agents/` directory to both Cloud Run (API server) and Vertex AI Agent Engine (individual agents).

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **ADK CLI** installed (`pip install google-adk`)
4. **Agents synced** to `agents/` directory (run `.\sync-agents.ps1` if needed)

## Deployment Options

### Option 1: Deploy API Server to Cloud Run

Deploys the FastAPI server that exposes all agents as a REST API (for ChatGPT integration).

```powershell
.\deploy-agents-api-to-cloud-run.ps1
```

**What it does:**
- Builds Docker image with agents-api-server.py
- Deploys to Cloud Run
- Exposes REST API endpoints for all agents
- Returns public URL for ChatGPT integration

**Configuration:**
```powershell
.\deploy-agents-api-to-cloud-run.ps1 `
  -ProjectId "aiagent-capstoneproject" `
  -Region "us-central1" `
  -ServiceName "adk-agents-api"
```

**After deployment:**
- Get the service URL from output
- Update `openapi.yaml` with the service URL
- Use in ChatGPT Custom GPT Actions

### Option 2: Deploy Individual Agents to Vertex AI Agent Engine

Deploys each agent separately to Vertex AI Agent Engine.

```powershell
.\deploy-agents-to-agent-engine.ps1
```

**What it does:**
- Discovers all agents from `agents/` directory
- Deploys each agent to Vertex AI Agent Engine
- Creates `.agent_engine_config.json` if missing
- Returns deployment summary

**Deploy specific agent:**
```powershell
.\deploy-agents-to-agent-engine.ps1 -Agent "sample-agent"
```

**Configuration:**
```powershell
.\deploy-agents-to-agent-engine.ps1 `
  -ProjectId "aiagent-capstoneproject" `
  -Region "us-east4" `
  -Agent "sample-agent"
```

**After deployment:**
- View agents in Vertex AI console
- Use `adk run agent_engine` to test
- Access via Vertex AI API

### Option 3: Deploy Both

Deploy API server to Cloud Run AND individual agents to Agent Engine:

```powershell
# Deploy API server
.\deploy-agents-api-to-cloud-run.ps1

# Deploy individual agents
.\deploy-agents-to-agent-engine.ps1
```

## Quick Start

### 1. Sync Agents (if needed)

```powershell
.\sync-agents.ps1
```

### 2. Deploy API Server to Cloud Run

```powershell
.\deploy-agents-api-to-cloud-run.ps1
```

Copy the service URL from output.

### 3. Update ChatGPT Integration

Update `openapi.yaml`:
```yaml
servers:
  - url: https://your-service-url.run.app
```

### 4. Deploy Agents to Vertex AI (Optional)

```powershell
.\deploy-agents-to-agent-engine.ps1
```

## Environment Variables

Both scripts read from `.env` file in project root. Required variables:

```env
GOOGLE_CLOUD_PROJECT=aiagent-capstoneproject
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json
GOOGLE_API_KEY=your-api-key
```

## Agent Configuration

Each agent in `agents/` directory can have `.agent_engine_config.json`:

```json
{
  "min_instances": 0,
  "max_instances": 1,
  "resource_limits": {
    "cpu": "1",
    "memory": "1Gi"
  }
}
```

If missing, default config is created automatically.

## Monitoring

### Cloud Run
- Console: https://console.cloud.google.com/run
- Logs: `gcloud run services logs read $ServiceName --region $Region`

### Vertex AI Agent Engine
- Console: https://console.cloud.google.com/vertex-ai/agents/agent-engines
- Logs: View in Cloud Console

## Troubleshooting

### "agents/ directory not found"
Run `.\sync-agents.ps1` to create the unified agents directory.

### "ADK CLI not found"
Install: `pip install google-adk`

### "Build failed"
- Check Docker is running (if building locally)
- Verify Cloud Build API is enabled
- Check project billing

### "Deployment failed"
- Verify project ID is correct
- Check IAM permissions
- Ensure APIs are enabled
- Check service account credentials

### "Agent not found"
- Verify agent has `agent.py` with `root_agent`
- Or has `root_agent.yaml`
- Check agent directory structure

## Cost Considerations

### Cloud Run
- Pay per request
- Free tier: 2 million requests/month
- Memory/CPU usage charges

### Vertex AI Agent Engine
- Pay per agent instance
- Minimum instances: 0 (scale to zero)
- Resource limits affect cost

## Next Steps

1. **Test API Server**: Use the service URL in `curl` or Postman
2. **Integrate with ChatGPT**: Update `openapi.yaml` and create Custom GPT
3. **Monitor Usage**: Check Cloud Console for metrics
4. **Scale as Needed**: Adjust Cloud Run and Agent Engine settings

## Files Created

- `deploy-agents-api-to-cloud-run.ps1` - Cloud Run deployment script
- `deploy-agents-to-agent-engine.ps1` - Agent Engine deployment script
- `Dockerfile.api` - Dockerfile for API server (auto-created)
- `DEPLOY_AGENTS.md` - This guide



