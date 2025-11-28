# Day3b: Memory Management Agents

This directory contains agents demonstrating long-term memory storage and retrieval from the Kaggle 5-day Agents course Day 3b.

## Agents

### 1. memory_agent.py
- **Features**: Manual memory storage and retrieval
- **Memory Service**: InMemoryMemoryService (keyword matching, no persistence)
- **Memory Tools**: `load_memory` (reactive) or `preload_memory` (proactive)
- **Use Case**: Learning memory mechanics, manual control

### 2. auto_memory_agent.py
- **Features**: Automatic memory storage using callbacks
- **Memory Service**: InMemoryMemoryService
- **Memory Tools**: `preload_memory` (proactive)
- **Callbacks**: `after_agent_callback` automatically saves sessions to memory
- **Use Case**: Production-ready automatic memory management

## Key Concepts

### Memory vs Session

| Feature | Session | Memory |
|---------|---------|--------|
| **Scope** | Single conversation | Across all conversations |
| **Lifespan** | Temporary (conversation thread) | Persistent (long-term storage) |
| **Use Case** | Short-term context | Long-term knowledge |
| **Analogy** | Application state | Database |

### Memory Retrieval Patterns

**Reactive (`load_memory`)**
- Agent decides when to search memory
- More efficient (saves tokens)
- Risk: Agent might forget to search

**Proactive (`preload_memory`)**
- Automatically searches before every turn
- Guaranteed context
- Less efficient (searches even when not needed)

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
# Run memory agent (interactive)
python run_memory_agent.py

# Run auto memory agent
python run_auto_memory_agent.py
```

## Usage Examples

### Memory Agent (Manual)

```python
from agents.memory_agent import runner, session_service, memory_service, USER_ID, APP_NAME
from google.genai import types
import asyncio

async def demo():
    # 1. Have a conversation
    query = types.Content(role="user", parts=[types.Part(text="My favorite color is blue-green")])
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id="conversation-01",
        new_message=query
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)
    
    # 2. Save session to memory
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id="conversation-01"
    )
    await memory_service.add_session_to_memory(session)
    
    # 3. Search memory
    search_response = await memory_service.search_memory(
        app_name=APP_NAME, user_id=USER_ID, query="What is the user's favorite color?"
    )
    print(f"Found {len(search_response.memories)} memories")
    
    # 4. Ask in new session (agent will use load_memory tool)
    query2 = types.Content(role="user", parts=[types.Part(text="What is my favorite color?")])
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id="new-session",  # Different session!
        new_message=query2
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)

asyncio.run(demo())
```

### Auto Memory Agent

```python
from agents.auto_memory_agent import runner, USER_ID
from google.genai import types
import asyncio

async def demo():
    # Conversation 1: Tell agent something
    query1 = types.Content(role="user", parts=[types.Part(text="I gifted a new toy to my nephew on his 1st birthday!")])
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id="auto-save-test",
        new_message=query1
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)
    # ✅ Automatically saved to memory via callback!
    
    # Conversation 2: Ask about it in NEW session
    query2 = types.Content(role="user", parts=[types.Part(text="What did I gift my nephew?")])
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id="auto-save-test-2",  # Different session!
        new_message=query2
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)
    # ✅ Memory automatically loaded via preload_memory!

asyncio.run(demo())
```

## Environment Variables

- `GOOGLE_API_KEY` - Required: Gemini API key
- `GOOGLE_CLOUD_PROJECT` - Required: GCP project ID
- `GOOGLE_CLOUD_LOCATION` - Optional: Default us-central1
- `AGENT_MODEL` - Optional: Default gemini-2.5-flash-lite
- `APP_NAME` - Optional: Default MemoryDemoApp
- `USER_ID` - Optional: Default demo_user
- `SESSION_SERVICE_TYPE` - Optional: inmemory or database (default: inmemory)
- `DB_URL` - Optional: Database URL (default: sqlite:///memory_data.db)
- `MEMORY_MODE` - Optional: reactive or proactive (default: reactive)

## Memory Service Types

**InMemoryMemoryService** (Current)
- Keyword matching
- No persistence (lost on restart)
- Good for learning and testing

**VertexAiMemoryBankService** (Production - Day 5)
- Semantic search (meaning-based)
- LLM-powered consolidation
- Persistent cloud storage
- Same API, better features

## Memory Operations

### Manual Storage
```python
# Get session
session = await session_service.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id="session-id"
)

# Save to memory
await memory_service.add_session_to_memory(session)
```

### Memory Search
```python
# Search memory
search_response = await memory_service.search_memory(
    app_name=APP_NAME,
    user_id=USER_ID,
    query="What is the user's favorite color?"
)

# Process results
for memory in search_response.memories:
    print(f"{memory.author}: {memory.content.parts[0].text}")
```

### Automatic Storage (Callbacks)
```python
async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Add to agent
agent = LlmAgent(
    ...,
    after_agent_callback=auto_save_to_memory
)
```

## Files Structure

```
Day3b/
├── agents/
│   ├── __init__.py
│   ├── memory_agent.py          # Manual memory management
│   └── auto_memory_agent.py      # Automatic memory with callbacks
├── run_memory_agent.py            # Interactive runner (manual)
├── run_auto_memory_agent.py       # Interactive runner (auto)
├── requirements.txt                # Python dependencies
├── env.template                   # Environment variable template
└── README.md                       # This file
```

## Next Steps

- Explore memory consolidation (Day 5 - Vertex AI Memory Bank)
- Test different memory retrieval patterns (reactive vs proactive)
- Integrate with your existing agents
- Deploy to production with Vertex AI Memory Bank


