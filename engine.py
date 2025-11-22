# engine.py

class Economy:
    # --- Tuning Constants (Calibration) ---
    # How much Real Rate affects Inflation (Higher = Faster drop in inflation)
    SENSITIVITY_INFLATION = 0.5  
    
    # How much Real Rate affects GDP (Higher = Faster recession)
    SENSITIVITY_GDP = 0.3        
    
    # Okun's Coefficient: How much GDP change affects Unemployment
    SENSITIVITY_UNEMPLOYMENT = 0.5 
    
    # Natural Limits
    MIN_INFLATION = -5.0
    MAX_INFLATION = 200.0  # Hyperinflation limit
    MIN_UNEMPLOYMENT = 3.0 # Structural unemployment
    MAX_UNEMPLOYMENT = 50.0

    def __init__(self):
        # Initial State
        self.inflation = 15.0      
        self.gdp_growth = 2.0      
        self.unemployment = 10.0   
        
        self.turn = 1
        
        # History initialization
        initial_rate = 15.0 
        self.policy_history = [initial_rate, initial_rate, initial_rate] 
        self.history = []

    def _calculate_effective_rate(self):
        rates = self.policy_history[-3:]
        if len(rates) < 3:
            return rates[-1]
        # Weighted average: 10% current, 30% prev, 60% prev-prev
        return (rates[-1] * 0.10) + (rates[-2] * 0.30) + (rates[-3] * 0.60)

    def next_turn(self, policy_interest_rate: float):
        # 1. Archive decision
        self.policy_history.append(policy_interest_rate)
        self._log_history(policy_interest_rate)

        # 2. Calculate Forces
        effective_rate = self._calculate_effective_rate()
        
        # Real Rate Gap: (Interest - Inflation)
        # Positive Gap = Contractionary (Cools economy)
        # Negative Gap = Expansionary (Heats economy)
        real_rate_gap = effective_rate - self.inflation

        # 3. Apply Physics
        # Change in Inflation
        inflation_delta = -(real_rate_gap * self.SENSITIVITY_INFLATION)
        self.inflation += inflation_delta

        # Change in GDP
        gdp_delta = -(real_rate_gap * self.SENSITIVITY_GDP)
        self.gdp_growth += gdp_delta

        # Change in Unemployment (Inverse to GDP)
        # Note: We use gdp_delta, assuming `gdp_growth` represents deviation from trend roughly
        unemployment_delta = -(gdp_delta * self.SENSITIVITY_UNEMPLOYMENT)
        self.unemployment += unemployment_delta

        # 4. Natural Decay / Stabilization (Mean Reversion)
        # If left untouched, extreme GDP growth tends to return to 2.0%
        # self.gdp_growth += (2.0 - self.gdp_growth) * 0.05 

        # 5. Apply Limits (Clamping)
        self.inflation = max(self.MIN_INFLATION, min(self.MAX_INFLATION, self.inflation))
        self.unemployment = max(self.MIN_UNEMPLOYMENT, min(self.MAX_UNEMPLOYMENT, self.unemployment))

        # 6. Advance
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