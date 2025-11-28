"""
Run Basic Session Agent
Interactive script to run the basic session agent
"""

import asyncio
from agents.basic_session_agent import runner
from google.genai import types
import os

USER_ID = os.getenv("USER_ID", "default")

async def main():
    """Run interactive session with the basic session agent"""
    print("=" * 60)
    print("Basic Session Agent - Interactive Mode")
    print("=" * 60)
    print("Simple stateful agent with in-memory sessions")
    print("Note: Sessions are lost when the agent restarts")
    print()
    
    session_id = input("Enter session ID (or press Enter for 'default'): ").strip() or "default"
    print(f"\nUsing session: {session_id}")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    while True:
        user_input = input("You > ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Convert to ADK Content format
        query = types.Content(role="user", parts=[types.Part(text=user_input)])
        
        print(f"\nAgent > ", end="", flush=True)
        
        # Stream the agent's response
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=query
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(text, end="", flush=True)
        
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())

