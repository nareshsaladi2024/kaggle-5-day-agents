# Day3a Session Agents - Deployment Guide

This guide provides step-by-step instructions for deploying the Day3a session management agents.

## Overview

Three agents are available:
1. **session_agent** - Full session management with state tools
2. **compaction_agent** - Automatic context compaction
3. **basic_session_agent** - Simple in-memory sessions

## Prerequisites

### Required
- Python 3.11+
- Docker Desktop (for Docker deployment)
- Google Cloud SDK (for Cloud Run deployment)
- Google AI API key

### Environment Variables
```powershell
$env:GOOGLE_API_KEY = "your-api-key"
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"  # Optional
```

## Local Development

### 1. Install Dependencies
```powershell
cd kaggle-5-day-agents\Day3a
pip install -r requirements.txt
```

### 2. Set Environment Variables
```powershell
# Option 1: Use .env file
Copy-Item env.template .env
# Edit .env with your credentials

# Option 2: Set PowerShell variables
$env:GOOGLE_API_KEY = "your-key"
$env:GOOGLE_CLOUD_PROJECT = "your-project"
```

### 3. Run Agents
```powershell
# Session agent (interactive)
python run_session_agent.py

# Compaction agent
python run_compaction_agent.py

# Basic session agent
python run_basic_session_agent.py
```

## Docker Desktop Deployment

### Quick Start
```powershell
# Deploy session agent
.\deploy-to-docker-desktop.ps1 -Agent session_agent

# Deploy compaction agent
.\deploy-to-docker-desktop.ps1 -Agent compaction_agent

# Deploy basic session agent
.\deploy-to-docker-desktop.ps1 -Agent basic_session_agent
```

### Using Docker Compose
```powershell
# Start all agents
docker-compose up -d

# View logs
docker-compose logs -f session-agent

# Stop all agents
docker-compose down
```

### Manual Docker Commands
```powershell
# Build image (from kaggle-5-day-agents directory)
docker build -f Day3a/Dockerfile.build -t day3a-session-agent:latest .

# Run container
docker run -it --rm `
  -e GOOGLE_API_KEY="your-key" `
  -e GOOGLE_CLOUD_PROJECT="your-project" `
  -v ${PWD}/Day3a/session_data.db:/app/session_data.db `
  day3a-session-agent:latest
```

### Stop Containers
```powershell
# Stop specific agent
.\deploy-to-docker-desktop.ps1 -Stop -Agent session_agent

# Or manually
docker stop day3a-session-agent
docker rm day3a-session-agent
```

## Google Cloud Run Deployment

### Prerequisites
1. Google Cloud SDK installed and authenticated
2. GCP project with billing enabled
3. Required APIs enabled:
   - Cloud Build API
   - Cloud Run API

### Deploy to Cloud Run
```powershell
# Set environment variables
$env:GOOGLE_API_KEY = "your-key"
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"

# Deploy session agent
.\deploy-to-cloud-run.ps1 -ProjectId "your-project-id" -Agent session_agent

# Deploy compaction agent
.\deploy-to-cloud-run.ps1 -ProjectId "your-project-id" -Agent compaction_agent -Region "us-central1"
```

### Access Deployed Service
```powershell
# Get service URL
gcloud run services describe day3a-session-agent `
  --region us-central1 `
  --format="value(status.url)" `
  --project your-project-id
```

### Update Deployment
```powershell
# Rebuild and redeploy
.\deploy-to-cloud-run.ps1 -ProjectId "your-project-id" -Agent session_agent
```

### Delete Service
```powershell
gcloud run services delete day3a-session-agent `
  --region us-central1 `
  --project your-project-id
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key | Required |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Required |
| `GOOGLE_CLOUD_LOCATION` | GCP region | `us-central1` |
| `AGENT_MODEL` | Gemini model name | `gemini-2.5-flash-lite` |
| `APP_NAME` | Application name | `session_app` |
| `USER_ID` | Default user ID | `default` |
| `SESSION_SERVICE_TYPE` | `inmemory` or `database` | `inmemory` |
| `DB_URL` | Database URL | `sqlite:///session_data.db` |
| `COMPACTION_INTERVAL` | Compaction trigger | `3` |
| `OVERLAP_SIZE` | Events to retain | `1` |

### Session Service Types

**InMemorySessionService**
- Fast, no persistence
- Lost on restart
- Good for testing

**DatabaseSessionService**
- Persistent storage
- Survives restarts
- SQLite for local, Cloud SQL for production

## Troubleshooting

### Docker Build Fails
- Ensure Docker Desktop is running
- Check that you're in the correct directory
- Verify `Dockerfile.build` exists

### Cloud Run Deployment Fails
- Verify gcloud is authenticated: `gcloud auth login`
- Check project ID is correct
- Ensure APIs are enabled
- Verify billing is enabled

### Agent Not Responding
- Check environment variables are set
- Verify API key is valid
- Check logs: `docker logs day3a-session-agent`

### Database Issues
- Ensure write permissions for database file
- Check database file path is correct
- For Cloud Run, consider Cloud SQL for persistence

## Next Steps

- Integrate with your existing agents
- Add custom session state management
- Configure context compaction for your use case
- Deploy to production with Cloud SQL

