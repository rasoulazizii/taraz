# engine.py

class Economy:
    def __init__(self):
        # Initial State (Normal Economy)
        self.inflation = 15.0      # %
        self.gdp_growth = 2.0      # %
        self.unemployment = 10.0   # %
        
        # Game State
        self.turn = 1
        
        # History & Memory
        # We assume the past interest rate was neutral (equal to inflation) to start stable
        initial_rate = 15.0 
        self.policy_history = [initial_rate, initial_rate, initial_rate] 
        self.history = []

    def _calculate_effective_rate(self):
        """
        Calculates the weighted average of the last 3 months' policy rates.
        Weights:
        - Current Month (t):   10% (Immediate shock)
        - Previous Month (t-1): 30%
        - Month (t-2):          60% (Full transmission)
        """
        # Get the last 3 rates (policy_history has the new rate appended already)
        rates = self.policy_history[-3:]
        
        # If we somehow have less than 3 items (shouldn't happen due to init), handle it
        if len(rates) < 3:
            return rates[-1]
            
        # rates[-1] is current, rates[-2] is prev, rates[-3] is prev-prev
        eff_rate = (rates[-1] * 0.10) + (rates[-2] * 0.30) + (rates[-3] * 0.60)
        return eff_rate

    def next_turn(self, policy_interest_rate: float):
        """
        Advance the simulation by one month.
        """
        # 1. Store the decision
        self.policy_history.append(policy_interest_rate)
        
        # 2. Log history before changes
        self._log_history(policy_interest_rate)

        # 3. Calculate Effective Rate (The actual force on the economy)
        effective_rate = self._calculate_effective_rate()

        # 4. Core Logic (Modified for Effective Rate)
        # Real Rate Gap: Difference between the "felt" rate and inflation
        real_rate_gap = effective_rate - self.inflation

        # -- Impact on Inflation --
        # Sensitivity 0.2: High rates reduce inflation slowly
        inflation_change = -(real_rate_gap * 0.2)
        self.inflation += inflation_change

        # -- Impact on GDP --
        # Sensitivity 0.1: High rates cool down growth
        gdp_change = -(real_rate_gap * 0.1)
        self.gdp_growth += gdp_change

        # -- Impact on Unemployment (Okun's Law) --
        # Inverse relation to GDP. 
        # If GDP drops by 1%, Unemployment rises by ~0.5%
        unemployment_change = -(gdp_change * 0.5)
        self.unemployment += unemployment_change

        # 5. Safety Clamps (Prevent unrealistic numbers for now)
        self.inflation = max(-5.0, self.inflation)
        self.unemployment = max(0.0, self.unemployment)
        self.unemployment = min(100.0, self.unemployment)

        # 6. Advance Turn
        self.turn += 1

        return {
            "turn": self.turn,
            "inflation": round(self.inflation, 2),
            "gdp_growth": round(self.gdp_growth, 2),
            "unemployment": round(self.unemployment, 2),
            "effective_rate": round(effective_rate, 2) # Returning this for UI visibility
        }

    def _log_history(self, policy_rate):
        snapshot = {
            "turn": self.turn,
            "inflation": self.inflation,
            "gdp_growth": self.gdp_growth,
            "unemployment": self.unemployment,
            "policy_rate": policy_rate
        }
        self.history.append(snapshot)