# Quick Deploy Guide - Vertex AI Agent Engine

## Why You Don't See Agents

Agents need to be **deployed** to Vertex AI Agent Engine before they appear in the console. The console at https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=aiagent-capstoneproject will be empty until you deploy.

## Prerequisites

1. **Install ADK CLI:**
   ```powershell
   pip install google-adk
   ```

2. **Verify authentication:**
   ```powershell
   gcloud auth login
   gcloud auth application-default login
   ```

3. **Set project:**
   ```powershell
   gcloud config set project aiagent-capstoneproject
   ```

## Deploy Agents

### Deploy All Agents
```powershell
cd C:\Capstone\kaggle-5-day-agents
.\deploy-to-agent-engine.ps1
```

### Deploy Specific Agent (e.g., sample-agent with weather tool)
```powershell
.\deploy-to-agent-engine.ps1 -Agent "Day1a/sample-agent"
```

### Deploy with Custom Region
```powershell
.\deploy-to-agent-engine.ps1 -Region "us-east4"
```

## What Gets Deployed

The script deploys these agents:
- helpful-assistant
- sample-agent (with weather tool)
- currency-agent
- image-agent
- shipping-agent
- session-agent
- memory-agent
- research-agent
- customer-support-agent
- weather-assistant

## After Deployment

1. **Wait 2-5 minutes** for agents to be ready
2. **Refresh the console** at:
   https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=aiagent-capstoneproject
3. **You should see** all deployed agents listed

## Troubleshooting

### "ADK CLI not found"
```powershell
pip install google-adk
```

### "Permission denied"
- Check IAM permissions in Cloud Console
- Ensure you have "Vertex AI User" role
- Run: `gcloud auth application-default login`

### "API not enabled"
The script enables APIs automatically, but you can also:
```powershell
gcloud services enable aiplatform.googleapis.com
gcloud services enable agentengine.googleapis.com
```

### Agents Still Not Showing
1. Check deployment logs for errors
2. Verify project ID is correct
3. Check region (us-east4 is recommended for Agent Engine)
4. Wait a few more minutes - deployment can take time

## Test Deployed Agent

Once deployed, test using ADK CLI:
```powershell
adk run agent_engine --project aiagent-capstoneproject --region us-east4 --agent-name sample-agent "What's the weather in London?"
```



