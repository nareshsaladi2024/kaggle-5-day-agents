"""
Run Memory Agent
Interactive script to run the memory management agent
"""

import asyncio
from agents.memory_agent import runner, USER_ID, APP_NAME, session_service, memory_service
from google.genai import types

async def run_session(
    runner_instance, user_queries: list[str] | str, session_id: str = "default"
):
    """Helper function to run queries in a session and display responses."""
    print(f"\n### Session: {session_id}")

    # Create or retrieve session
    try:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    # Convert single query to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Process each query
    for query in user_queries:
        print(f"\nUser > {query}")
        query_content = types.Content(role="user", parts=[types.Part(text=query)])

        # Stream agent response
        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session.id, new_message=query_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"Agent > {text}")
    
    return session

async def main():
    """Run interactive session with the memory agent"""
    print("=" * 60)
    print("Memory Agent - Interactive Mode")
    print("=" * 60)
    print()
    print("This agent demonstrates long-term memory storage and retrieval.")
    print("Memory persists across different sessions!")
    print()
    
    session_id = input("Enter session ID (or press Enter for 'default'): ").strip() or "default"
    print(f"\nUsing session: {session_id}")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'save' to save current session to memory")
    print("Type 'search <query>' to search memory")
    print()
    
    while True:
        user_input = input("You > ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Handle special commands
        if user_input.lower() == 'save':
            try:
                session = await session_service.get_session(
                    app_name=APP_NAME, user_id=USER_ID, session_id=session_id
                )
                await memory_service.add_session_to_memory(session)
                print("✅ Session saved to memory!")
            except Exception as e:
                print(f"❌ Error saving to memory: {e}")
            continue
        
        if user_input.lower().startswith('search '):
            query = user_input[7:].strip()
            try:
                search_response = await memory_service.search_memory(
                    app_name=APP_NAME, user_id=USER_ID, query=query
                )
                print(f"\n🔍 Search Results: Found {len(search_response.memories)} memories")
                for memory in search_response.memories[:5]:  # Show first 5
                    if memory.content and memory.content.parts:
                        text = memory.content.parts[0].text[:100]
                        print(f"  [{memory.author}]: {text}...")
            except Exception as e:
                print(f"❌ Error searching memory: {e}")
            continue
        
        # Normal conversation
        query = types.Content(role="user", parts=[types.Part(text=user_input)])
        
        print(f"\nAgent > ", end="", flush=True)
        
        # Stream the agent's response
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=query
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(text, end="", flush=True)
        
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())


