# Docker Deployment Guide for Kaggle 5-Day Agents

This guide explains how to deploy and run all agents using Docker Desktop with ADK web server.

## Prerequisites

1. **Docker Desktop** installed and running
2. **.env file** configured in Day1a (copied to all days)
3. **Service account JSON** file (if using Vertex AI)

## Quick Start

### 1. Ensure .env files are configured

The `.env` file from `Day1a/helpful_assistant/.env` has been copied to all day directories. Verify your credentials are set:

```bash
# Check .env file in Day1a
cat Day1a/.env
```

Required variables:
- `GOOGLE_API_KEY` (or use service account)
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_APPLICATION_CREDENTIALS` (path to service_account.json)

### 2. Build and run with Docker Compose

```bash
# Build and start the container
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Access ADK Web UI

Once the container is running, open your browser to:
- **http://localhost:8080**

The ADK web interface will show all discoverable agents from all days:
- Day1a: helpful_assistant, sample-agent
- Day1b: ResearchAgent, WriterAgent, and many more
- Day2a: CurrencyAgent
- Day2b: image_agent, shipping_agent
- Day3a: session_agent, compaction_agent, basic_session_agent
- Day3b: memory_agent, auto_memory_agent
- Day4a: ResearchAgent
- Day4b: home_automation_agent
- Day5a: CustomerSupportAgent, ProductCatalogAgent
- Day5b: WeatherAssistant

## Docker Commands

### View logs
```bash
docker-compose logs -f adk-web
```

### Stop the container
```bash
docker-compose down
```

### Rebuild after code changes
```bash
docker-compose up --build
```

### Access container shell
```bash
docker exec -it kaggle-5-day-agents-web /bin/bash
```

### Check if ADK web is running
```bash
docker ps
# Look for kaggle-5-day-agents-web container
```

## Troubleshooting

### Port 8080 already in use
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8081:8080"  # Use 8081 instead of 8080
```

### Environment variables not loading
1. Check that `.env` files exist in each day directory
2. Verify the file paths in `docker-compose.yml` volumes section
3. Check container logs: `docker-compose logs adk-web`

### Agents not showing in ADK web
1. Check container logs for import errors
2. Verify all `agent.py` files exist in day directories
3. Ensure `root_agent` is defined in each agent module

### Service account authentication
If using service account JSON:
1. Ensure `service_account.json` exists in project root
2. Mount path is correct in `docker-compose.yml`
3. Set `GOOGLE_APPLICATION_CREDENTIALS=/app/service_account.json` in .env

## File Structure

```
kaggle-5-day-agents/
├── Dockerfile                 # Main Docker image definition
├── docker-compose.yml         # Docker Compose configuration
├── .dockerignore              # Files to exclude from Docker build
├── requirements.txt           # Python dependencies
├── service_account.json       # Google Cloud service account (if used)
├── Day1a/
│   ├── .env                  # Environment variables
│   ├── agent.py              # ADK discovery wrapper
│   └── helpful_assistant/
│       └── agent.py          # Actual agent
├── Day1b/
│   ├── .env
│   ├── agent.py
│   └── [multiple agents]/
└── [Day2a-Day5b]/            # Similar structure
```

## Environment Variables

All agents use `.env` files in their respective day directories. The Docker setup:
1. Mounts `.env` files as read-only volumes
2. Sets environment variables from the root `.env` (if using docker-compose env file)
3. Agents use `load_dotenv()` to load from their day directory

## Notes

- Database files (`.db`) are mounted as volumes to persist data
- All agents are discoverable via ADK web when `root_agent` is defined at module level
- The ADK web server runs on port 8080 inside the container
- Logs are available via `docker-compose logs`

