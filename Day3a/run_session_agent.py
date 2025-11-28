"""
Run Session Agent
Interactive script to run the session management agent
"""

import asyncio
from agents.session_agent import runner, USER_ID
from google.genai import types

async def main():
    """Run interactive session with the agent"""
    print("=" * 60)
    print("Session Agent - Interactive Mode")
    print("=" * 60)
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

