# engine.py

class Economy:
    # --- Tuning Constants (Fixed Logic) ---
    
    # 1. Targets
    TARGET_INFLATION = 3.0
    TARGET_GDP_GROWTH = 3.0
    TARGET_UNEMPLOYMENT = 5.0

    # 2. Sensitivities
    SENSITIVITY_INFLATION = 0.05  
    SENSITIVITY_GDP = 0.05       
    
    # Increased: Recession now hurts employment more
    SENSITIVITY_UNEMPLOYMENT = 0.25 
    
    # 3. Gravity (Mean Reversion)
    GRAVITY_GDP = 0.2          
    GRAVITY_INFLATION = 0.02   
    
    # Decreased: Unemployment takes longer to heal naturally
    GRAVITY_UNEMPLOYMENT = 0.02 

    # 4. Hard Limits
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

    def _calculate_effective_rate(self):
        rates = self.policy_history[-3:]
        if len(rates) < 3:
            return rates[-1]
        return (rates[-1] * 0.10) + (rates[-2] * 0.30) + (rates[-3] * 0.60)

    def next_turn(self, policy_interest_rate: float):
        self.policy_history.append(policy_interest_rate)
        self._log_history(policy_interest_rate)

        effective_rate = self._calculate_effective_rate()
        real_rate_gap = effective_rate - self.inflation

        # A) Inflation
        inflation_delta = -(real_rate_gap * self.SENSITIVITY_INFLATION)
        inflation_gravity = (self.TARGET_INFLATION - self.inflation) * self.GRAVITY_INFLATION
        self.inflation += (inflation_delta + inflation_gravity)

        # B) GDP
        gdp_pressure = -(real_rate_gap * self.SENSITIVITY_GDP)
        gdp_gravity = (self.TARGET_GDP_GROWTH - self.gdp_growth) * self.GRAVITY_GDP
        self.gdp_growth += (gdp_pressure + gdp_gravity)

        # C) Unemployment (Okun's Law)
        gdp_gap = self.TARGET_GDP_GROWTH - self.gdp_growth
        unemployment_delta = (gdp_gap * self.SENSITIVITY_UNEMPLOYMENT)
        unemployment_gravity = (self.TARGET_UNEMPLOYMENT - self.unemployment) * self.GRAVITY_UNEMPLOYMENT
        
        self.unemployment += (unemployment_delta + unemployment_gravity)

        # D) Clamping
        self.inflation = max(self.MIN_INFLATION, min(self.MAX_INFLATION, self.inflation))
        self.unemployment = max(self.MIN_UNEMPLOYMENT, min(self.MAX_UNEMPLOYMENT, self.unemployment))
        self.gdp_growth = max(self.MIN_GDP, min(self.MAX_GDP, self.gdp_growth))

        self.turn += 1

        return {
            "turn": self.turn,
            "inflation": round(self.inflation, 2),
            "gdp_growth": round(self.gdp_growth, 2),
            "unemployment": round(self.unemployment, 2),
            "effective_rate": round(effective_rate, 2)
        }

    def _log_history(self, policy_rate):
        self.history.append({
            "turn": self.turn,
            "inflation": self.inflation,
            "gdp": self.gdp_growth,
            "unemployment": self.unemployment,
            "rate": policy_rate
        })