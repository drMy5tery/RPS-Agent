"""
Rock-Paper-Scissors-Plus Agent Package

Exposes the root_agent for use with ADK CLI or programmatic runners.
"""

# Import state and tools (no ADK dependency)
from .game_state import GameState, create_initial_state
from .tools import validate_move, resolve_round, update_game_state

# Try to import the agent (requires google-adk)
try:
    from .agent import root_agent
    __all__ = [
        "root_agent",
        "GameState",
        "create_initial_state",
        "validate_move",
        "resolve_round",
        "update_game_state",
    ]
except ImportError:
    # google-adk not installed
    __all__ = [
        "GameState",
        "create_initial_state",
        "validate_move",
        "resolve_round",
        "update_game_state",
    ]
