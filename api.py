# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import Economy
from typing import List, Dict

app = FastAPI(title="Taraz API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_instance = Economy()

class PolicyInput(BaseModel):
    interest_rate: float

class EventModel(BaseModel):
    title: str
    desc: str
    type: str
    impact: Dict[str, float]

class GameState(BaseModel):
    turn: int
    inflation: float
    gdp_growth: float
    unemployment: float
    effective_rate: float
    events: List[EventModel] = []
    
    # New Fields
    political_tension: float = 0.0
    gov_message: str = ""

@app.get("/")
def read_root():
    return {"status": "online", "game": "Taraz Simulator"}

@app.get("/state", response_model=GameState)
def get_state():
    return {
        "turn": game_instance.turn,
        "inflation": round(game_instance.inflation, 2),
        "gdp_growth": round(game_instance.gdp_growth, 2),
        "unemployment": round(game_instance.unemployment, 2),
        "effective_rate": round(game_instance._calculate_effective_rate(), 2),
        "events": game_instance.active_events,
        "political_tension": round(game_instance.political_tension, 1),
        "gov_message": game_instance.gov_message
    }

@app.post("/next_turn", response_model=GameState)
def next_turn(policy: PolicyInput):
    if not (-10.0 <= policy.interest_rate <= 100.0):
        raise HTTPException(status_code=400, detail="Interest rate must be between -10 and 100")
    new_state = game_instance.next_turn(policy.interest_rate)
    return new_state

@app.post("/reset")
def reset_game():
    global game_instance
    game_instance = Economy()
    return {"message": "Game reset successfully", "turn": 1}