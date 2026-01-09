# Rock-Paper-Scissors-Plus AI Game Referee

An AI-powered game referee chatbot for "Rock-Paper-Scissors-Plus" built with **Google ADK (Agent Development Kit)**.

## Game Rules

- **Best of 3 rounds** (exactly 3 rounds maximum)
- **Valid moves**: `rock`, `paper`, `scissors`, `bomb`
- **Outcomes**:
  - rock > scissors > paper > rock
  - bomb beats ALL other moves
  - bomb vs bomb → draw
- **Bomb constraint**: Each player can use bomb **once per game**
- **Invalid input**: Counts as a wasted round (neither player scores)

## Quick Start

```bash
# 1. Clone and navigate to the project
cd RPS-Agent

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API key
set GOOGLE_API_KEY=your_google_ai_api_key  # Windows
# export GOOGLE_API_KEY=your_key  # Linux/Mac

# 5. Run the game
python main.py
```

## Example Gameplay

### Normal Match
```
==================================================
  ROCK-PAPER-SCISSORS-PLUS
==================================================

Starting game...

Welcome! I'm your AI Referee for Rock-Paper-Scissors-Plus.
Rules: Best of 3 rounds. Valid moves: rock, paper, scissors, bomb.
Rock > Scissors > Paper > Rock. Bomb beats all except another bomb.
Each player can use bomb ONCE per game. Invalid moves waste the round.

Your move: rock

Round: 1
User move: rock
Bot move: scissors
Winner: User
Score: User 1 - Bot 0

Your move: paper

Round: 2
User move: paper
Bot move: rock
Winner: User
Score: User 2 - Bot 0

Your move: scissors

Round: 3
User move: scissors
Bot move: paper
Winner: User
Score: User 3 - Bot 0

Final Result: User wins!

Game Over! Thanks for playing!
```

### Invalid Move Scenario
```
Your move: hello

Round: 1
User move: hello (INVALID)
Bot move: rock
Winner: Bot
Score: User 0 - Bot 1
(Invalid move wastes the round - bot wins by default)
```

### Double Bomb Attempt
```
Your move: bomb

Round: 1
User move: bomb
Bot move: scissors
Winner: User
Score: User 1 - Bot 0

Your move: bomb

Round: 2
User move: bomb (INVALID - already used)
Bot move: rock
Winner: Bot  
Score: User 1 - Bot 1
(Second bomb attempt is invalid - round wasted)
```

## Project Structure

```
RPS-Agent/
├── main.py                 # CLI runner (entry point)
├── requirements.txt        # Dependencies
├── README.md
└── rps_agent/
    ├── __init__.py         # Package exports
    ├── agent.py            # ADK Agent definition
    ├── game_state.py       # Pydantic state models
    └── tools.py            # ADK tools (validate, resolve, update)
```

## Architecture

### Game State Model

```python
GameState:
  round_number: int      # 1-3 (4 = ended)
  user_score: int        # User's wins
  bot_score: int         # Bot's wins
  user_bomb_used: bool   # Bomb constraint tracking
  bot_bomb_used: bool    
  game_over: bool        
  history: List[RoundResult]
```

State is stored in ADK's `session.state` for persistence across conversation turns.

### Agent + Tool Design

**Single Agent with Tool Separation of Concerns:**

| Tool | Layer | Responsibility |
|------|-------|----------------|
| `validate_move` | Intent Understanding | Parse input, check validity, verify bomb usage |
| `resolve_round` | Game Logic | Apply rules, determine round winner |
| `update_game_state` | State Management | Update scores, track bombs, check game end |

The agent orchestrates these tools based on its instructions, ensuring:
- All state changes happen through tools (not just in prompts)
- Clear separation between understanding, logic, and state
- Deterministic, testable game resolution

### Flow

```
User Input → Agent → validate_move → resolve_round → update_game_state → Response
```

## ADK Integration

This project uses:
- `google.adk.agents.Agent` - LLM-powered agent with tool access
- `google.adk.runners.InMemoryRunner` - Session-aware execution
- `google.adk.sessions.InMemorySessionService` - State persistence
- Pydantic models for structured data

## Tradeoffs & Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single agent vs multi-agent | Simpler architecture; tool separation provides adequate modularity |
| Random bot strategy | Fair gameplay; could be made strategic |
| In-memory state | Per requirements; no DB/external storage |
| Pydantic models | Type safety, validation, easy serialization |

## Future Improvements

With more time, I would add:
1. **Unit tests** for each tool function
2. **Smarter bot AI** (track user patterns, strategic bomb timing)
3. **Web UI** using ADK's web runner
4. **Configurable game modes** (best of 5, no bomb mode, etc.)
5. **Game history persistence** across sessions

## Requirements

- Python 3.10+
- Google API Key (Gemini access)
- See `requirements.txt` for packages