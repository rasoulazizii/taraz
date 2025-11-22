# engine.py
import random

class Economy:
    # --- Tuning Constants ---
    TARGET_INFLATION = 3.0
    TARGET_GDP_GROWTH = 3.0
    TARGET_UNEMPLOYMENT = 5.0

    SENSITIVITY_INFLATION = 0.05  
    SENSITIVITY_GDP = 0.05       
    SENSITIVITY_UNEMPLOYMENT = 0.25 
    
    GRAVITY_GDP = 0.2          
    GRAVITY_INFLATION = 0.02   
    GRAVITY_UNEMPLOYMENT = 0.02 

    MIN_INFLATION = -5.0
    MAX_INFLATION = 100.0 
    MIN_UNEMPLOYMENT = 2.0
    MAX_UNEMPLOYMENT = 40.0
    MIN_GDP = -10.0 
    MAX_GDP = 15.0   

    def __init__(self):
        self.inflation = 15.0      
        self.gdp_growth = 2.0      
        self.unemployment = 10.0   
        
        self.turn = 1
        
        initial_rate = 15.0 
        self.policy_history = [initial_rate, initial_rate, initial_rate] 
        self.history = []
        
        # Event System State
        self.active_events = [] # List of events happening this turn

    def _calculate_effective_rate(self):
        rates = self.policy_history[-3:]
        if len(rates) < 3:
            return rates[-1]
        return (rates[-1] * 0.10) + (rates[-2] * 0.30) + (rates[-3] * 0.60)

    def _process_random_events(self):
        """
        Roll dice to see if a random event occurs.
        Returns a list of event dictionaries.
        """
        triggered = []
        
        # 1. Oil Shock (Negative Supply Shock) - 5% Chance
        if random.random() < 0.05:
            event = {
                "title": "شوک نفتی",
                "desc": "قیمت جهانی نفت افزایش یافت. هزینه تولید بالا رفت.",
                "type": "negative",
                "impact": {"inflation": 4.0, "gdp": -2.0}
            }
            triggered.append(event)
            # Apply Impact Immediately
            self.inflation += 4.0
            self.gdp_growth -= 2.0

        # 2. Tech Boom (Positive Supply Shock) - 5% Chance
        elif random.random() < 0.05:
            event = {
                "title": "جهش فناوری",
                "desc": "استارتاپ‌های جدید بهره‌وری را افزایش دادند.",
                "type": "positive",
                "impact": {"inflation": -1.0, "gdp": 3.0}
            }
            triggered.append(event)
            self.inflation -= 1.0
            self.gdp_growth += 3.0

        # 3. Labor Strike (Conditional Trigger)
        # If Inflation > 25%, 20% chance of strike
        if self.inflation > 25.0 and random.random() < 0.20:
             event = {
                "title": "اعتصاب کارگران",
                "desc": "کارگران به دلیل تورم بالا دست از کار کشیدند.",
                "type": "severe",
                "impact": {"gdp": -3.0, "unemployment": 2.0}
            }
             triggered.append(event)
             self.gdp_growth -= 3.0
             self.unemployment += 2.0

        return triggered

    def next_turn(self, policy_interest_rate: float):
        self.policy_history.append(policy_interest_rate)
        self._log_history(policy_interest_rate)

        effective_rate = self._calculate_effective_rate()
        real_rate_gap = effective_rate - self.inflation

        # 1. Core Physics
        inflation_delta = -(real_rate_gap * self.SENSITIVITY_INFLATION)
        inflation_gravity = (self.TARGET_INFLATION - self.inflation) * self.GRAVITY_INFLATION
        self.inflation += (inflation_delta + inflation_gravity)

        gdp_pressure = -(real_rate_gap * self.SENSITIVITY_GDP)
        gdp_gravity = (self.TARGET_GDP_GROWTH - self.gdp_growth) * self.GRAVITY_GDP
        self.gdp_growth += (gdp_pressure + gdp_gravity)

        gdp_gap = self.TARGET_GDP_GROWTH - self.gdp_growth
        unemployment_delta = (gdp_gap * self.SENSITIVITY_UNEMPLOYMENT)
        unemployment_gravity = (self.TARGET_UNEMPLOYMENT - self.unemployment) * self.GRAVITY_UNEMPLOYMENT
        self.unemployment += (unemployment_delta + unemployment_gravity)

        # 2. Process Events (This modifies variables on top of physics)
        self.active_events = self._process_random_events()

        # 3. Clamping
        self.inflation = max(self.MIN_INFLATION, min(self.MAX_INFLATION, self.inflation))
        self.unemployment = max(self.MIN_UNEMPLOYMENT, min(self.MAX_UNEMPLOYMENT, self.unemployment))
        self.gdp_growth = max(self.MIN_GDP, min(self.MAX_GDP, self.gdp_growth))

        self.turn += 1

        return {
            "turn": self.turn,
            "inflation": round(self.inflation, 2),
            "gdp_growth": round(self.gdp_growth, 2),
            "unemployment": round(self.unemployment, 2),
            "effective_rate": round(effective_rate, 2),
            "events": self.active_events # Send to API
        }

    def _log_history(self, policy_rate):
        self.history.append({
            "turn": self.turn,
            "inflation": self.inflation,
            "gdp": self.gdp_growth,
            "unemployment": self.unemployment,
            "rate": policy_rate
        })