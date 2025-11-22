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
    money_printer: float = 0.0

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
    gov_type: str = "دولت"
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

@app.get("/")
def read_root():
    return {"status": "online", "game": "Taraz Simulator"}

@app.get("/state", response_model=GameState)
def get_state():
    advisors = game_instance._get_advisor_report(game_instance.policy_history[-1])
    
    # --- FIX: Use persisted game over status ---
    go_status = game_instance.game_over_status
    
    return {
        "turn": game_instance.turn,
        "inflation": round(game_instance.inflation, 2),
        "gdp_growth": round(game_instance.gdp_growth, 2),
        "unemployment": round(game_instance.unemployment, 2),
        "effective_rate": round(game_instance._calculate_effective_rate(), 2),
        "events": game_instance.active_events,
        "political_tension": round(game_instance.political_tension, 1),
        "gov_message": game_instance.gov_message,
        "exchange_rate": round(game_instance.exchange_rate, 0),
        "fx_change": round(game_instance.fx_change_rate, 2),
        "money_supply_index": round(game_instance.money_supply_index, 1),
        "gov_type": game_instance.gov.name,
        "gov_desc": game_instance.gov.profile["desc"],
        
        # Correctly mapped fields
        "is_game_over": go_status["is_game_over"],
        "game_over_reason": go_status["reason"],
        "game_over_type": go_status["type"],
        
        "advisors": advisors
    }

@app.post("/next_turn", response_model=GameState)
def next_turn(policy: PolicyInput):
    if not (-10.0 <= policy.interest_rate <= 100.0):
        raise HTTPException(status_code=400, detail="Interest rate invalid")
    if not (-50.0 <= policy.money_printer <= 50.0):
        raise HTTPException(status_code=400, detail="Money printer invalid")

    new_state = game_instance.next_turn(policy.interest_rate, policy.money_printer)
    return new_state

@app.post("/forecast", response_model=List[ForecastPoint])
def get_forecast(policy: PolicyInput):
    forecast = game_instance.simulate_future(policy.interest_rate, policy.money_printer)
    return forecast

@app.post("/reset")
def reset_game():
    global game_instance
    game_instance = Economy()
    return {"message": "Game reset successfully", "turn": 1}