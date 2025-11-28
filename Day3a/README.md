# Day3a: Session Management Agents

This directory contains agents demonstrating session management capabilities from the Kaggle 5-day Agents course Day 3a.

## Agents

### 1. session_agent.py
- **Features**: Session state management with user info tools
- **Session Service**: DatabaseSessionService (SQLite) or InMemorySessionService
- **Tools**: `save_userinfo`, `retrieve_userinfo`
- **Use Case**: Persistent conversations with user context

### 2. compaction_agent.py
- **Features**: Automatic context compaction for long conversations
- **Session Service**: DatabaseSessionService
- **Configuration**: Compaction interval and overlap size
- **Use Case**: Long-running conversations with automatic summarization

### 3. basic_session_agent.py
- **Features**: Simple stateful agent with in-memory sessions
- **Session Service**: InMemorySessionService
- **Use Case**: Quick prototyping and testing

## Quick Start

### Prerequisites

1. Install dependencies:
```powershell
pip install -r requirements.txt
```

2. Set up environment variables:
```powershell
# Copy template
Copy-Item env.template .env

# Edit .env with your credentials
# Or set environment variables directly:
$env:GOOGLE_API_KEY = "your-api-key"
$env:GOOGLE_CLOUD_PROJECT = "aiagent-capstoneproject"
```

### Local Development

```powershell
# Run session agent (interactive)
python run_session_agent.py

# Run compaction agent
python run_compaction_agent.py

# Run basic session agent
python run_basic_session_agent.py
```

### Docker Desktop

```powershell
# Deploy session agent
.\deploy-to-docker-desktop.ps1 -Agent session_agent

# Deploy compaction agent
.\deploy-to-docker-desktop.ps1 -Agent compaction_agent

# Or use docker-compose for all agents
docker-compose up -d
```

### Google Cloud Run

```powershell
# Set environment variables
$env:GOOGLE_API_KEY = "your-api-key"
$env:GOOGLE_CLOUD_PROJECT = "aiagent-capstoneproject"

# Deploy to Cloud Run
.\deploy-to-cloud-run.ps1 -ProjectId "aiagent-capstoneproject" -Agent session_agent
```

## Environment Variables

- `GOOGLE_API_KEY` - Required: Gemini API key
- `GOOGLE_CLOUD_PROJECT` - Required: GCP project ID
- `GOOGLE_CLOUD_LOCATION` - Optional: Default us-central1
- `AGENT_MODEL` - Optional: Default gemini-2.5-flash-lite
- `SESSION_SERVICE_TYPE` - Optional: inmemory or database (default: inmemory)
- `DB_URL` - Optional: Database URL (default: sqlite:///session_data.db)
- `COMPACTION_INTERVAL` - Optional: Compaction trigger interval (default: 3)
- `OVERLAP_SIZE` - Optional: Events to retain for overlap (default: 1)

## Usage Examples

### Session Agent

```python
from agents.session_agent import runner, USER_ID
from google.genai import types
import asyncio

async def chat():
    query = types.Content(role="user", parts=[types.Part(text="Hi, I'm Sam from Poland")])
    
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id="my-session",
        new_message=query
    ):
        if event.content and event.content.parts:
            print(event.content.parts[0].text)

asyncio.run(chat())
```

### Compaction Agent

```python
from agents.compaction_agent import runner, USER_ID
from google.genai import types
import asyncio

async def long_conversation():
    queries = [
        "What is AI?",
        "Tell me more about machine learning",
        "What are neural networks?",
        "Explain deep learning"
    ]
    
    for query_text in queries:
        query = types.Content(role="user", parts=[types.Part(text=query_text)])
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id="compaction-demo",
            new_message=query
        ):
            if event.content and event.content.parts:
                print(event.content.parts[0].text)

asyncio.run(long_conversation())
```

## Docker Deployment

### Build Image

```powershell
docker build -t day3a-session-agent:latest .
```

### Run Container

```powershell
docker run -it --rm \
  -e GOOGLE_API_KEY="your-key" \
  -e GOOGLE_CLOUD_PROJECT="your-project" \
  -v ${PWD}/session_data.db:/app/session_data.db \
  day3a-session-agent:latest
```

### Docker Compose

```powershell
# Start all agents
docker-compose up -d

# View logs
docker-compose logs -f session-agent

# Stop all
docker-compose down
```

## Cloud Run Deployment

### Prerequisites

- Google Cloud SDK installed
- Docker installed
- GCP project with billing enabled

### Deploy

```powershell
.\deploy-to-cloud-run.ps1 -ProjectId "your-project" -Agent session_agent
```

### Access

After deployment, get the service URL:

```powershell
gcloud run services describe day3a-session-agent --region us-central1 --format="value(status.url)"
```

## Session Data

### Database Location

- **Local**: `session_data.db` (SQLite file)
- **Docker**: Mounted volume at `/app/session_data.db`
- **Cloud Run**: Ephemeral (consider using Cloud SQL for persistence)

### Inspecting Sessions

```python
from agents.session_agent import session_service, APP_NAME, USER_ID

# Get session
session = await session_service.get_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id="my-session"
)

# Inspect state
print(session.state)

# Inspect events
for event in session.events:
    print(event)
```

## Files Structure

```
Day3a/
├── agents/
│   ├── session_agent.py          # Full session management
│   ├── compaction_agent.py        # Context compaction
│   └── basic_session_agent.py      # Basic sessions
├── run_session_agent.py            # Interactive runner
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Multi-agent compose
├── requirements.txt                # Python dependencies
├── deploy-to-docker-desktop.ps1    # Docker Desktop deployment
├── deploy-to-cloud-run.ps1         # Cloud Run deployment
└── README.md                       # This file
```

## Next Steps

- Explore session state management
- Test context compaction with long conversations
- Deploy to production with Cloud Run
- Integrate with your existing agents

