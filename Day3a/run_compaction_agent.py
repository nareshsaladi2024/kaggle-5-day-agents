"""
Run Compaction Agent
Interactive script to run the context compaction agent
"""

import asyncio
from agents.compaction_agent import runner
from google.genai import types
import os

USER_ID = os.getenv("USER_ID", "default")

async def main():
    """Run interactive session with the compaction agent"""
    print("=" * 60)
    print("Compaction Agent - Interactive Mode")
    print("=" * 60)
    print("This agent automatically compacts conversation history")
    print("Compaction triggers every 3 turns by default")
    print()
    
    session_id = input("Enter session ID (or press Enter for 'compaction-demo'): ").strip() or "compaction-demo"
    print(f"\nUsing session: {session_id}")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    turn_count = 0
    
    while True:
        user_input = input("You > ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        turn_count += 1
        print(f"[Turn {turn_count}]")
        
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

