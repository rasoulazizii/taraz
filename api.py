from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import Economy
from typing import List, Dict, Any, Union

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
    money_printer: float = 0.0
    lang: str = "en" # Input language for POST

class EventModel(BaseModel):
    title: str
    desc: str
    type: str
    impact: Dict[str, float]

class AdvisorModel(BaseModel):
    name: str
    msg: str
    type: str

class GameState(BaseModel):
    turn: int
    inflation: float
    gdp_growth: float
    unemployment: float
    effective_rate: float
    events: List[EventModel] = []
    political_tension: float = 0.0
    gov_message: str = ""
    exchange_rate: float = 50000.0
    fx_change: float = 0.0
    money_supply_index: float = 100.0
    gov_type: str = "Government"
    gov_desc: str = ""
    is_game_over: bool = False
    game_over_reason: str = ""
    game_over_type: str = "none" 
    advisors: List[AdvisorModel] = []

class ForecastPoint(BaseModel):
    turn: int
    inflation: float
    gdp_growth: float
    unemployment: float

# --- Localization Helper ---
def localize(data: Any, lang: str) -> Any:
    """Recursively translate dicts with 'en'/'fa' keys to strings"""
    if isinstance(data, dict):
        # If it's a translation dict (has 'en' and 'fa'), pick one
        if "en" in data and "fa" in data and len(data) == 2:
            return data.get(lang, data["en"])
        # Otherwise, traverse deeper
        return {k: localize(v, lang) for k, v in data.items()}
    elif isinstance(data, list):
        return [localize(i, lang) for i in data]
    else:
        return data

@app.get("/")
def read_root():
    return {"status": "online", "game": "Taraz Simulator"}

@app.get("/state", response_model=GameState)
def get_state(lang: str = Query("en", regex="^(en|fa)$")):
    # Get Raw State (with dicts)
    raw_state = game_instance.next_turn(game_instance.policy_history[-1], 0, is_simulation=True)
    
    # Re-inject persisted advisors (simulation above might reset them)
    raw_state["advisors"] = game_instance._get_advisor_report(game_instance.policy_history[-1])
    
    # Re-inject persisted game over logic
    go = game_instance.game_over_status
    raw_state["is_game_over"] = go["is_game_over"]
    raw_state["game_over_reason"] = go["reason"]
    raw_state["game_over_type"] = go["type"]
    
    # Re-inject events (simulation clears them, we want last turn's events)
    raw_state["events"] = game_instance.active_events

    # Localize
    localized_state = localize(raw_state, lang)
    return localized_state

@app.post("/next_turn", response_model=GameState)
def next_turn(policy: PolicyInput):
    if not (-10.0 <= policy.interest_rate <= 100.0):
        raise HTTPException(status_code=400, detail="Interest rate invalid")
    if not (-50.0 <= policy.money_printer <= 50.0):
        raise HTTPException(status_code=400, detail="Money printer invalid")

    raw_state = game_instance.next_turn(policy.interest_rate, policy.money_printer)
    
    # Localize
    localized_state = localize(raw_state, policy.lang)
    return localized_state

@app.post("/forecast", response_model=List[ForecastPoint])
def get_forecast(policy: PolicyInput):
    forecast = game_instance.simulate_future(policy.interest_rate, policy.money_printer)
    return forecast

@app.post("/reset")
def reset_game():
    global game_instance
    game_instance = Economy()
    return {"message": "Game reset successfully", "turn": 1}