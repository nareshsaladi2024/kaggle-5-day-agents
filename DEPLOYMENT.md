# Deployment Guide for Kaggle 5-Day Agents

This guide explains how to deploy agents to Vertex AI Agent Engine and Google Cloud Run.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
   ```powershell
   gcloud auth login
   gcloud auth application-default login
   ```
3. **ADK CLI** installed (for Agent Engine deployment)
   ```powershell
   pip install google-adk
   ```
4. **Docker** installed and running (for Cloud Run)
5. **.env file** configured with your credentials

## Deployment Options

### Option 1: Deploy to Vertex AI Agent Engine

Deploys agents to Vertex AI Agent Engine for production use with auto-scaling.

**Features:**
- Auto-scaling based on demand
- Managed infrastructure
- Pay-per-use pricing
- Best for production workloads

**Deploy all agents:**
```powershell
.\deploy-to-agent-engine.ps1
```

**Deploy specific agent:**
```powershell
.\deploy-to-agent-engine.ps1 -Agent "Day1a/helpful_assistant"
```

**With custom project/region:**
```powershell
.\deploy-to-agent-engine.ps1 -ProjectId "my-project" -Region "us-east4"
```

**Available regions:**
- `us-east4` (default)
- `us-west1`
- `europe-west1`
- `europe-west4`

**What gets deployed:**
- Day1a: helpful_assistant, sample-agent
- Day2a: CurrencyAgent
- Day2b: image_agent, shipping_agent
- Day3a: session_agent
- Day3b: memory_agent
- Day4a: ResearchAgent
- Day5a: CustomerSupportAgent
- Day5b: WeatherAssistant

### Option 2: Deploy to Google Cloud Run

Deploys ADK web server to Cloud Run as a containerized service.

**Features:**
- HTTP endpoint for ADK web UI
- Container-based deployment
- Auto-scaling
- Good for web-based access

**Deploy:**
```powershell
.\deploy-to-cloud-run.ps1
```

**With custom project/region:**
```powershell
.\deploy-to-cloud-run.ps1 -ProjectId "my-project" -Region "us-central1"
```

**Access:**
After deployment, you'll get a URL like:
```
https://kaggle-5-day-agents-xxxxx-uc.a.run.app
```

Open this URL in your browser to access the ADK web UI with all agents.

## Configuration

### Environment Variables

Both scripts read from `.env` file. Required variables:

```env
GOOGLE_CLOUD_PROJECT=aiagent-capstoneproject
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json
ADK_LOG_LEVEL=DEBUG
```

### Agent Engine Config

Each agent can have a `.agent_engine_config.json` file for custom configuration:

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

If not present, the script creates a default config.

## Post-Deployment

### Agent Engine

1. **Wait 2-5 minutes** for agents to be ready
2. **View in console:**
   ```
   https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=YOUR_PROJECT
   ```
3. **Test agents** using ADK CLI or console
4. **Monitor usage** in Cloud Console

### Cloud Run

1. **Access ADK Web UI** at the provided URL
2. **View in console:**
   ```
   https://console.cloud.google.com/run?project=YOUR_PROJECT
   ```
3. **Monitor logs:**
   ```powershell
   gcloud run services logs read kaggle-5-day-agents --region us-central1
   ```

## Troubleshooting

### Agent Engine Deployment Fails

1. **Check ADK CLI:**
   ```powershell
   adk --version
   ```

2. **Verify APIs enabled:**
   ```powershell
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable agentengine.googleapis.com
   ```

3. **Check authentication:**
   ```powershell
   gcloud auth list
   gcloud auth application-default print-access-token
   ```

### Cloud Run Deployment Fails

1. **Check Docker:**
   ```powershell
   docker version
   ```

2. **Verify APIs enabled:**
   ```powershell
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

3. **Check build logs:**
   ```powershell
   gcloud builds list --limit=5
   ```

### Common Issues

**"Permission denied"**
- Ensure service account has required roles
- Check IAM permissions in Cloud Console

**"API not enabled"**
- Run the script again (it enables APIs automatically)
- Or enable manually in Cloud Console

**"Image build failed"**
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check Cloud Build logs

## Cost Considerations

### Agent Engine
- Pay per request/execution
- Auto-scales to zero when not in use
- Good for variable workloads

### Cloud Run
- Pay per request and compute time
- Minimum instances can be set to 0
- Good for web-based access

## Next Steps

1. **Test deployed agents** using ADK CLI or console
2. **Set up monitoring** in Cloud Console
3. **Configure alerts** for errors or high usage
4. **Review costs** in Cloud Billing

## Additional Resources

- [Vertex AI Agent Engine Docs](https://cloud.google.com/vertex-ai/docs/agent-builder/agent-engine/overview)
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [ADK Deployment Guide](https://google.github.io/adk-docs/deployment/)

