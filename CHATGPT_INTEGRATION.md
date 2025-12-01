# Integrating ADK Agents with ChatGPT

This guide shows you how to add your ADK agents to ChatGPT and run them.

## Method 1: Custom GPT with API Actions (Recommended)

### Step 1: Start the API Server

```powershell
# Install dependencies
pip install fastapi uvicorn python-multipart

# Run the API server
python agents-api-server.py
```

The server will run at `http://localhost:8000`

### Step 2: Expose Server Publicly

For ChatGPT to access your API, you need a public URL. Options:

#### Option A: Use ngrok (Quick Testing)
```powershell
# Install ngrok: https://ngrok.com/download
ngrok http 8000
# Copy the public URL (e.g., https://abc123.ngrok.io)
```

#### Option B: Deploy to Cloud Run (Production)
```powershell
# Build and deploy
gcloud run deploy adk-agents-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Step 3: Create Custom GPT in ChatGPT

1. Go to [ChatGPT Custom GPTs](https://chat.openai.com/gpts)
2. Click "Create" → "Create a GPT"
3. Configure your GPT:
   - **Name**: "ADK Agents Assistant"
   - **Description**: "Access to Google ADK agents for various tasks"
   - **Instructions**: 
     ```
     You are an assistant that can use various ADK agents:
     - helpful_assistant: General questions and weather
     - sample-agent: Sample agent with weather tool
     - currency_agent: Currency conversion
     - research_agent: Research and information gathering
     - customer_support_agent: Customer support
     - weather_assistant: Weather information
     
     Use the /chat API endpoint to interact with agents.
     ```

4. **Add Action (API)**:
   - Click "Create new action"
   - **Authentication**: None (or API key if you add auth)
   - **Schema**: Use OpenAPI schema (see below)

### Step 4: OpenAPI Schema for ChatGPT

Create an `openapi.yaml` file:

```yaml
openapi: 3.1.0
info:
  title: ADK Agents API
  description: API for Google ADK agents
  version: 1.0.0
servers:
  - url: https://your-api-url.com  # Your ngrok or Cloud Run URL
paths:
  /chat:
    post:
      summary: Chat with an ADK agent
      operationId: chatWithAgent
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: The user's message
                agent_name:
                  type: string
                  description: Name of the agent to use
                  enum: [helpful_assistant, sample-agent, currency_agent, research_agent, customer_support_agent, weather_assistant]
                conversation_id:
                  type: string
                  description: Optional conversation ID for context
      responses:
        '200':
          description: Agent response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                  agent_name:
                    type: string
                  conversation_id:
                    type: string
```

Paste this schema into ChatGPT's Action configuration.

## Method 2: Direct API Calls from ChatGPT

If you have ChatGPT Plus with Code Interpreter, you can call the API directly:

```python
import requests

# Chat with helpful_assistant
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What's the weather in London?",
        "agent_name": "helpful_assistant"
    }
)

print(response.json()["response"])
```

## Method 3: Deploy to Vertex AI Agent Engine

Deploy agents to Vertex AI and access via API:

```powershell
# Deploy agents
.\deploy-to-agent-engine.ps1

# Get API endpoint from Vertex AI console
# Use the endpoint in ChatGPT Actions
```

## Testing the Integration

### Test Locally

```powershell
# Start server
python agents-api-server.py

# In another terminal, test the API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in London?", "agent_name": "helpful_assistant"}'
```

### Test with ChatGPT

1. Create your Custom GPT
2. Add the API action
3. Ask: "Use the helpful_assistant agent to tell me about the weather in London"
4. ChatGPT will call your API and return the agent's response

## Available Agents

- **helpful_assistant**: General questions + weather (`get_weather_for_city`)
- **sample-agent**: Sample agent + weather (`get_weather_in_london`)
- **currency_agent**: Currency conversion
- **image_agent**: Image processing
- **shipping_agent**: Shipping workflows
- **research_agent**: Research and citations
- **customer_support_agent**: Customer support
- **product_catalog_agent**: Product catalog queries
- **weather_assistant**: Weather information

## API Endpoints

- `GET /` - Health check
- `GET /agents` - List all agents
- `POST /chat` - Chat with an agent
- `POST /chat/{agent_name}` - Chat with specific agent
- `GET /agents/{agent_name}/info` - Get agent information
- `GET /docs` - API documentation (Swagger UI)

## Security Considerations

1. **Add Authentication**: Use API keys or OAuth
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **HTTPS**: Always use HTTPS in production
4. **Input Validation**: Validate and sanitize inputs
5. **CORS**: Restrict CORS origins in production

## Troubleshooting

### ChatGPT can't reach your API
- Ensure server is publicly accessible (use ngrok or cloud deployment)
- Check firewall settings
- Verify CORS is enabled

### Agent not found errors
- Check agent paths in `agents-api-server.py`
- Verify agent directories exist
- Check agent.py files have `root_agent` defined

### Import errors
- Ensure all dependencies are installed
- Check Python path includes project root
- Verify .env files are in place

## Next Steps

1. Deploy API server to production
2. Create Custom GPTs for specific use cases
3. Add more agents to the API
4. Implement conversation context/memory
5. Add authentication and rate limiting



