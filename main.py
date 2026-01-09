#!/usr/bin/env python3
"""
Rock-Paper-Scissors-Plus CLI Runner

Simple conversational loop using ADK InMemoryRunner for state persistence.
Run with: python main.py

Requires GOOGLE_API_KEY environment variable to be set.
"""

import asyncio
import os
import sys
import uuid

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from rps_agent import root_agent, create_initial_state


async def main():
    """Main conversational loop for the RPS-Plus game."""
    
    # Verify API key is set
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Set it with: set GOOGLE_API_KEY=your_key (Windows)")
        print("         or: export GOOGLE_API_KEY=your_key (Linux/Mac)")
        sys.exit(1)
    
    # Initialize the runner with the agent
    runner = InMemoryRunner(
        agent=root_agent,
        app_name="rps_plus_game",
    )
    
    # Generate session identifiers
    user_id = "player1"
    session_id = str(uuid.uuid4())
    
    # Create session before running (InMemoryRunner has its own session service)
    # Access the internal session service to create the session
    session = await runner.session_service.create_session(
        app_name="rps_plus_game",
        user_id=user_id,
        session_id=session_id,
        state=create_initial_state(),
    )
    
    print("=" * 50)
    print("  ROCK-PAPER-SCISSORS-PLUS")
    print("=" * 50)
    print()
    
    # Initial greeting - let agent explain rules
    print("Starting game...\n")
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="Start the game and explain the rules.")],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(part.text)
    except Exception as e:
        print(f"Error during initial prompt: {e}")
        print("\nNote: If you're seeing a rate limit error, wait a few minutes and try again.")
        print("You can also try a different model by editing agent.py")
        return
    
    print()
    
    # Track rounds locally (since session state may not be directly accessible)
    round_count = 0
    max_rounds = 3
    
    # Game loop
    while round_count < max_rounds:
        # Get user input
        try:
            user_input = input("\nYour move: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGame interrupted. Goodbye!")
            break
        
        if not user_input:
            print("Please enter a move (rock, paper, scissors, or bomb)")
            continue
        
        if user_input.lower() in ("quit", "exit", "q"):
            print("Thanks for playing!")
            break
        
        # Process user input through the agent
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=types.Content(
                    role="user",
                    parts=[types.Part(text=user_input)],
                ),
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            print(part.text)
                            # Check if the agent mentioned a round completion
                            if "Round:" in part.text or "round" in part.text.lower():
                                round_count += 1
        except Exception as e:
            print(f"Error: {e}")
            print("Continuing game...")
            continue
    
    print("\nGame Over! Thanks for playing!")
    
    # Clean up
    await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
