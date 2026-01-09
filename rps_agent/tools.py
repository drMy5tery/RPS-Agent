"""
Rock-Paper-Scissors-Plus ADK Tools

Implements three tools with clear separation of concerns:
1. validate_move - Intent Understanding (parse and validate user input)
2. resolve_round - Game Logic (determine round winner)
3. update_game_state - State Management (update scores and track progress)
"""

import random
from typing import Any

from .game_state import (
    VALID_MOVES,
    GameState,
    RoundResult,
    MoveValidation,
    create_initial_state,
)


def validate_move(move: str, is_user: bool, game_state: dict) -> dict:
    """
    Validates a player's move against game rules.
    
    This tool handles the Intent Understanding layer:
    - Parses and normalizes user input
    - Checks if move is in valid move list
    - Validates bomb usage (once per player per game)
    
    Args:
        move: The move to validate (e.g., "rock", "PAPER", "bomb")
        is_user: True if validating user's move, False for bot's move
        game_state: Current game state dictionary
        
    Returns:
        Dictionary with validation result:
        {
            "is_valid": bool,
            "move": str,
            "normalized_move": str or None,
            "error_message": str or None,
            "is_bomb_already_used": bool
        }
    """
    # Normalize the move
    normalized = move.lower().strip() if isinstance(move, str) else ""
    
    # Check if move is in valid moves list
    if normalized not in VALID_MOVES:
        return MoveValidation(
            is_valid=False,
            move=move,
            normalized_move=None,
            error_message=f"Invalid move '{move}'. Valid moves: rock, paper, scissors, bomb",
            is_bomb_already_used=False,
        ).model_dump()
    
    # Check bomb usage constraint
    if normalized == "bomb":
        bomb_used = game_state.get("user_bomb_used", False) if is_user else game_state.get("bot_bomb_used", False)
        if bomb_used:
            player = "User" if is_user else "Bot"
            return MoveValidation(
                is_valid=False,
                move=move,
                normalized_move=None,
                error_message=f"{player} has already used their bomb. Choose another move.",
                is_bomb_already_used=True,
            ).model_dump()
    
    # Valid move
    return MoveValidation(
        is_valid=True,
        move=move,
        normalized_move=normalized,
        error_message=None,
        is_bomb_already_used=False,
    ).model_dump()


def resolve_round(user_move: str, bot_move: str) -> dict:
    """
    Determines the winner of a round based on game rules.
    
    This tool handles the Game Logic layer:
    - rock > scissors
    - scissors > paper
    - paper > rock
    - bomb beats ALL other moves
    - bomb vs bomb → draw
    
    Args:
        user_move: User's move (normalized, lowercase)
        bot_move: Bot's move (normalized, lowercase)
        
    Returns:
        Dictionary with resolution result:
        {
            "user_move": str,
            "bot_move": str,
            "winner": "user" | "bot" | "draw",
            "explanation": str
        }
    """
    # Normalize moves
    user = user_move.lower().strip()
    bot = bot_move.lower().strip()
    
    # Handle invalid moves (treat as automatic loss)
    user_valid = user in VALID_MOVES
    bot_valid = bot in VALID_MOVES
    
    if not user_valid and not bot_valid:
        return {
            "user_move": user_move,
            "bot_move": bot_move,
            "winner": "draw",
            "explanation": "Both moves invalid - round is a draw.",
        }
    elif not user_valid:
        return {
            "user_move": user_move,
            "bot_move": bot_move,
            "winner": "bot",
            "explanation": f"User's move '{user_move}' is invalid. Bot wins by default.",
        }
    elif not bot_valid:
        return {
            "user_move": user_move,
            "bot_move": bot_move,
            "winner": "user",
            "explanation": f"Bot's move '{bot_move}' is invalid. User wins by default.",
        }
    
    # Both moves are valid - apply game rules
    
    # Same move = draw
    if user == bot:
        return {
            "user_move": user,
            "bot_move": bot,
            "winner": "draw",
            "explanation": f"Both played {user}. It's a draw!",
        }
    
    # Bomb logic
    if user == "bomb":
        return {
            "user_move": user,
            "bot_move": bot,
            "winner": "user",
            "explanation": f"User's bomb beats {bot}!",
        }
    if bot == "bomb":
        return {
            "user_move": user,
            "bot_move": bot,
            "winner": "bot",
            "explanation": f"Bot's bomb beats {user}!",
        }
    
    # Standard RPS logic
    wins_against = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock",
    }
    
    if wins_against.get(user) == bot:
        return {
            "user_move": user,
            "bot_move": bot,
            "winner": "user",
            "explanation": f"{user.capitalize()} beats {bot}!",
        }
    else:
        return {
            "user_move": user,
            "bot_move": bot,
            "winner": "bot",
            "explanation": f"{bot.capitalize()} beats {user}!",
        }


def update_game_state(
    game_state: dict,
    user_move: str,
    bot_move: str,
    winner: str,
    user_move_valid: bool = True,
    bot_move_valid: bool = True,
) -> dict:
    """
    Updates the game state after a round.
    
    This tool handles the State Management layer:
    - Updates round number
    - Updates scores based on winner
    - Tracks bomb usage
    - Checks for game end (after round 3)
    - Records round in history
    
    Args:
        game_state: Current game state dictionary
        user_move: User's move this round
        bot_move: Bot's move this round
        winner: Round winner ("user", "bot", or "draw")
        user_move_valid: Whether user's move was valid
        bot_move_valid: Whether bot's move was valid
        
    Returns:
        Updated game state dictionary
    """
    state = GameState.from_dict(game_state)
    current_round = state.round_number
    
    # Update scores
    if winner == "user":
        state.user_score += 1
    elif winner == "bot":
        state.bot_score += 1
    # draw: no score change
    
    # Track bomb usage
    user_normalized = user_move.lower().strip() if isinstance(user_move, str) else ""
    bot_normalized = bot_move.lower().strip() if isinstance(bot_move, str) else ""
    
    if user_normalized == "bomb" and user_move_valid:
        state.user_bomb_used = True
    if bot_normalized == "bomb" and bot_move_valid:
        state.bot_bomb_used = True
    
    # Record round in history
    round_result = RoundResult(
        round_number=current_round,
        user_move=user_move,
        bot_move=bot_move,
        user_move_valid=user_move_valid,
        bot_move_valid=bot_move_valid,
        winner=winner,
    )
    state.history.append(round_result)
    
    # Advance round
    state.round_number = current_round + 1
    
    # Check game end (after round 3)
    if state.round_number > 3:
        state.game_over = True
    
    return state.to_dict()


def generate_bot_move(game_state: dict) -> str:
    """
    Generates a random valid move for the bot.
    
    Args:
        game_state: Current game state dictionary
        
    Returns:
        Bot's move as a string
    """
    available_moves = ["rock", "paper", "scissors"]
    
    # Add bomb if not used yet
    if not game_state.get("bot_bomb_used", False):
        # Bot has 20% chance to use bomb if available
        if random.random() < 0.2:
            return "bomb"
    
    return random.choice(available_moves)


def get_final_result(game_state: dict) -> dict:
    """
    Determines the final game result.
    
    Args:
        game_state: Final game state dictionary
        
    Returns:
        Dictionary with final result:
        {
            "user_score": int,
            "bot_score": int,
            "result": "User wins" | "Bot wins" | "Draw"
        }
    """
    user_score = game_state.get("user_score", 0)
    bot_score = game_state.get("bot_score", 0)
    
    if user_score > bot_score:
        result = "User wins"
    elif bot_score > user_score:
        result = "Bot wins"
    else:
        result = "Draw"
    
    return {
        "user_score": user_score,
        "bot_score": bot_score,
        "result": result,
    }
