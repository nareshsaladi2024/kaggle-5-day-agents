# Day3a Session Agents - Quick Start

## 🚀 5-Minute Setup

### 1. Install Dependencies
```powershell
cd kaggle-5-day-agents\Day3a
pip install -r requirements.txt
```

### 2. Set API Key
```powershell
$env:GOOGLE_API_KEY = "your-api-key"
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"
```

### 3. Run Agent
```powershell
python run_session_agent.py
```

## 🐳 Docker Quick Start

```powershell
# Build and run
.\deploy-to-docker-desktop.ps1 -Agent session_agent

# View logs
docker logs -f day3a-session-agent

# Stop
.\deploy-to-docker-desktop.ps1 -Stop -Agent session_agent
```

## ☁️ Cloud Run Quick Start

```powershell
.\deploy-to-cloud-run.ps1 -ProjectId "your-project-id" -Agent session_agent
```

## 📚 Available Agents

- **session_agent** - Full session management with state tools
- **compaction_agent** - Automatic context compaction
- **basic_session_agent** - Simple in-memory sessions

See [README.md](README.md) for detailed documentation.

