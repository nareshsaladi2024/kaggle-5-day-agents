"""
Run Auto Memory Agent
Interactive script to run the automatic memory storage agent
"""

import asyncio
from agents.auto_memory_agent import runner, USER_ID, APP_NAME
from google.genai import types

async def run_session(
    runner_instance, user_queries: list[str] | str, session_id: str = "default"
):
    """Helper function to run queries in a session and display responses."""
    print(f"\n### Session: {session_id}")

    # Convert single query to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Process each query
    for query in user_queries:
        print(f"\nUser > {query}")
        query_content = types.Content(role="user", parts=[types.Part(text=query)])

        # Stream agent response
        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session_id, new_message=query_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"Agent > {text}")

async def main():
    """Run interactive session with the auto memory agent"""
    print("=" * 60)
    print("Auto Memory Agent - Interactive Mode")
    print("=" * 60)
    print()
    print("This agent automatically saves conversations to memory after each turn.")
    print("Memory is also automatically loaded before each turn (proactive mode).")
    print()
    
    session_id = input("Enter session ID (or press Enter for 'default'): ").strip() or "default"
    print(f"\nUsing session: {session_id}")
    print("Type 'quit' or 'exit' to end the conversation")
    print()
    print("💡 Tip: Try asking about something in one session, then ask about it")
    print("   again in a different session to see memory retrieval in action!")
    print()
    
    while True:
        user_input = input("You > ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Normal conversation (memory is automatically saved and loaded)
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
        print("✅ Conversation automatically saved to memory!")

if __name__ == "__main__":
    asyncio.run(main())

