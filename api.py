# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import Economy

# 1. Initialize the App
app = FastAPI(title="Taraz API", version="0.1.0")

# 2. Enable CORS (So Frontend can talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Initialize Game Engine (Global State)
# In a real multi-user game, this would be a database.
# For now, one global game instance for simplicity.
game_instance = Economy()

# --- Data Models (Input/Output Schema) ---
class PolicyInput(BaseModel):
    interest_rate: float

class GameState(BaseModel):
    turn: int
    inflation: float
    gdp_growth: float
    unemployment: float
    effective_rate: float

# --- Endpoints ---

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "online", "game": "Taraz Simulator"}

@app.get("/state", response_model=GameState)
def get_state():
    """Get current game dashboard."""
    return {
        "turn": game_instance.turn,
        "inflation": round(game_instance.inflation, 2),
        "gdp_growth": round(game_instance.gdp_growth, 2),
        "unemployment": round(game_instance.unemployment, 2),
        # Recalculate effective rate just for display
        "effective_rate": round(game_instance._calculate_effective_rate(), 2)
    }

@app.post("/next_turn", response_model=GameState)
def next_turn(policy: PolicyInput):
    """
    Submit policy decision and advance time.
    """
    # Validation: Rate must be reasonable
    if not (-10.0 <= policy.interest_rate <= 100.0):
        raise HTTPException(status_code=400, detail="Interest rate must be between -10 and 100")

    # Execute Logic
    new_state = game_instance.next_turn(policy.interest_rate)
    return new_state

@app.post("/reset")
def reset_game():
    """Restart the game from scratch."""
    global game_instance
    game_instance = Economy()
    return {"message": "Game reset successfully", "turn": 1}