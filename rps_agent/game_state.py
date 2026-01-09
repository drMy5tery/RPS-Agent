"""
Rock-Paper-Scissors-Plus Game State Model

Defines Pydantic schemas for game state, round results, and move validation.
State is managed via ADK session.state for persistence across turns.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# Valid moves in the game
VALID_MOVES = {"rock", "paper", "scissors", "bomb"}

# Move type alias
MoveType = Literal["rock", "paper", "scissors", "bomb"]
WinnerType = Literal["user", "bot", "draw"]


class RoundResult(BaseModel):
    """Stores the result of a single round."""
    round_number: int = Field(..., ge=1, le=3, description="Round number (1-3)")
    user_move: str = Field(..., description="User's move (may be invalid)")
    bot_move: str = Field(..., description="Bot's move")
    user_move_valid: bool = Field(True, description="Whether user move was valid")
    bot_move_valid: bool = Field(True, description="Whether bot move was valid")
    winner: WinnerType = Field(..., description="Winner of the round")


class MoveValidation(BaseModel):
    """Result of move validation."""
    is_valid: bool = Field(..., description="Whether the move is valid")
    move: str = Field(..., description="The attempted move")
    normalized_move: Optional[str] = Field(None, description="Normalized move if valid")
    error_message: Optional[str] = Field(None, description="Error message if invalid")
    is_bomb_already_used: bool = Field(False, description="True if bomb was already used")


class GameState(BaseModel):
    """
    Complete game state for Rock-Paper-Scissors-Plus.
    
    Tracks:
    - Round progression (1-3)
    - Scores for user and bot
    - Bomb usage per player (once per game)
    - Game over status
    - History of all rounds
    """
    round_number: int = Field(1, ge=1, le=4, description="Current round (1-3, 4 means ended)")
    user_score: int = Field(0, ge=0, description="User's score")
    bot_score: int = Field(0, ge=0, description="Bot's score")
    user_bomb_used: bool = Field(False, description="Has user used their bomb?")
    bot_bomb_used: bool = Field(False, description="Has bot used their bomb?")
    game_over: bool = Field(False, description="Is the game finished?")
    history: List[RoundResult] = Field(default_factory=list, description="Round history")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for session state storage."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """Create GameState from dictionary."""
        if not data:
            return cls()
        # Handle history with RoundResult objects
        if "history" in data and data["history"]:
            data["history"] = [
                RoundResult(**r) if isinstance(r, dict) else r 
                for r in data["history"]
            ]
        return cls(**data)


def create_initial_state() -> dict:
    """Create initial game state as dictionary."""
    return GameState().to_dict()
