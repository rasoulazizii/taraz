import random

class Economy:
    # --- Tuning Constants (Re-Re-Calibrated) ---
    TARGET_INFLATION = 3.0
    TARGET_GDP_GROWTH = 3.0
    TARGET_UNEMPLOYMENT = 5.0

    # Sensitivities (Much Lower for Stability)
    SENSITIVITY_INFLATION = 0.03  # Reduced from 0.05 (Inflation is harder to kill)
    SENSITIVITY_GDP = 0.04        # Reduced from 0.05 (Recession hits slower)
    SENSITIVITY_UNEMPLOYMENT = 0.25 
    
    # External Sector (Drastically Reduced)
    GLOBAL_INTEREST_RATE = 2.0
    SENSITIVITY_FX = 0.1          # Reduced from 0.5 (Currency is less volatile)
    PASS_THROUGH_COEF = 0.2       # Reduced from 0.4 (Import inflation is milder)
    
    SENSITIVITY_MONEY_INFLATION = 0.15
    SENSITIVITY_MONEY_GDP = 0.15
    SENSITIVITY_MONEY_FX = 0.2    # Printing money hurts FX, but not instantly fatal

    # Gravity (Increased Resilience)
    GRAVITY_GDP = 0.3             # Increased from 0.2 (Economy heals faster)
    GRAVITY_INFLATION = 0.05      # Increased from 0.02 (Prices tend to stabilize)
    GRAVITY_UNEMPLOYMENT = 0.05   # Increased from 0.02 (Jobs return faster)

    # Limits
    MIN_INFLATION = -5.0
    MAX_INFLATION = 200.0
    MIN_UNEMPLOYMENT = 2.0
    MAX_UNEMPLOYMENT = 50.0
    MIN_GDP = -15.0
    MAX_GDP = 15.0

    def __init__(self):
        self.inflation = 15.0
        self.gdp_growth = 2.0
        self.unemployment = 10.0
        self.exchange_rate = 50000.0
        self.fx_change_rate = 0.0
        self.money_supply_index = 100.0
        
        self.turn = 1
        initial_rate = 15.0
        self.policy_history = [initial_rate, initial_rate, initial_rate]
        self.history = []
        self.active_events = []
        
        self.political_tension = 0.0
        self.gov_message = "دولت وضعیت را رصد می‌کند."

    def _calculate_effective_rate(self):
        rates = self.policy_history[-3:]
        if len(rates) < 3: return rates[-1]
        return (rates[-1] * 0.10) + (rates[-2] * 0.30) + (rates[-3] * 0.60)

    def _process_random_events(self):
        triggered = []
        if random.random() < 0.05:
            triggered.append({
                "title": "شوک نفتی", "desc": "افزایش جهانی قیمت نفت.", 
                "type": "negative", "impact": {"inflation": 4.0, "gdp": -2.0}
            })
            self.inflation += 4.0
            self.gdp_growth -= 2.0
        elif random.random() < 0.05:
            triggered.append({
                "title": "جهش فناوری", "desc": "افزایش بهره‌وری.", 
                "type": "positive", "impact": {"inflation": -1.0, "gdp": 3.0}
            })
            self.inflation -= 1.0
            self.gdp_growth += 3.0
        if self.inflation > 20.0 and random.random() < 0.20:
             triggered.append({
                "title": "اعتصاب کارگران", "desc": "اعتراض به گرانی.", 
                "type": "severe", "impact": {"gdp": -3.0, "unemployment": 2.0}
            })
             self.gdp_growth -= 3.0
             self.unemployment += 2.0
        return triggered

    def _update_political_tension(self, policy_rate):
        tension_change = 0.0
        self.gov_message = "دولت فعلاً سکوت کرده است."

        if policy_rate > 15.0: # Increased tolerance threshold to 15%
            diff = policy_rate - 15.0
            tension_change += (diff * 0.4) # Slightly less angry
            if diff > 10: self.gov_message = "هشدار: نرخ بهره بسیار بالاست!"

        if self.unemployment > 10.0: # Increased tolerance to 10%
            diff = self.unemployment - 10.0
            tension_change += (diff * 0.8)
            if diff > 5: self.gov_message = "هشدار: بیکاری بحرانی است."

        if self.fx_change_rate > 5.0:
             tension_change += 3.0 # Less angry about FX
             self.gov_message = "هشدار: سقوط ارزش پول ملی!"

        if policy_rate <= 15.0 and self.unemployment <= 10.0 and self.fx_change_rate < 3.0:
            tension_change -= 3.0 # Faster forgiveness
            self.gov_message = "دولت رضایت دارد."

        self.political_tension += tension_change
        self.political_tension = max(0.0, min(100.0, self.political_tension))
        
        if self.political_tension > 85.0:
            self.gov_message = "‼️ اولتیماتوم: خطر برکناری!"

    def next_turn(self, policy_interest_rate: float, money_printer: float = 0.0):
        self.policy_history.append(policy_interest_rate)
        self._log_history(policy_interest_rate)

        effective_rate = self._calculate_effective_rate()
        self.money_supply_index += money_printer
        
        # --- FX Logic ---
        rate_differential = effective_rate - self.GLOBAL_INTEREST_RATE
        natural_depreciation = (self.inflation - 2.0) * 0.05 # Slower natural depreciation
        capital_flow_effect = rate_differential * self.SENSITIVITY_FX
        money_supply_shock = money_printer * self.SENSITIVITY_MONEY_FX
        
        self.fx_change_rate = natural_depreciation - capital_flow_effect + money_supply_shock
        self.exchange_rate = self.exchange_rate * (1 + (self.fx_change_rate / 100.0))
        self.exchange_rate = max(1000.0, self.exchange_rate)

        # --- Core Physics ---
        real_rate_gap = effective_rate - self.inflation

        # Inflation
        inflation_delta = -(real_rate_gap * self.SENSITIVITY_INFLATION)
        import_inflation = self.fx_change_rate * self.PASS_THROUGH_COEF
        monetary_inflation = money_printer * self.SENSITIVITY_MONEY_INFLATION
        inflation_gravity = (self.TARGET_INFLATION - self.inflation) * self.GRAVITY_INFLATION
        self.inflation += (inflation_delta + import_inflation + monetary_inflation + inflation_gravity)

        # GDP
        gdp_pressure = -(real_rate_gap * self.SENSITIVITY_GDP)
        export_boost = self.fx_change_rate * 0.03 # Reduced export boost
        monetary_stimulus = money_printer * self.SENSITIVITY_MONEY_GDP
        gdp_gravity = (self.TARGET_GDP_GROWTH - self.gdp_growth) * self.GRAVITY_GDP
        self.gdp_growth += (gdp_pressure + export_boost + monetary_stimulus + gdp_gravity)

        # Unemployment
        gdp_gap = self.TARGET_GDP_GROWTH - self.gdp_growth
        unemployment_delta = (gdp_gap * self.SENSITIVITY_UNEMPLOYMENT)
        unemployment_gravity = (self.TARGET_UNEMPLOYMENT - self.unemployment) * self.GRAVITY_UNEMPLOYMENT
        self.unemployment += (unemployment_delta + unemployment_gravity)

        # Events & Politics
        self.active_events = self._process_random_events()
        self._update_political_tension(policy_interest_rate)

        # Clamping
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
            "events": self.active_events,
            "political_tension": round(self.political_tension, 1),
            "gov_message": self.gov_message,
            "exchange_rate": round(self.exchange_rate, 0),
            "fx_change": round(self.fx_change_rate, 2),
            "money_supply_index": round(self.money_supply_index, 1)
        }

    def _log_history(self, policy_rate):
        self.history.append({
            "turn": self.turn,
            "inflation": self.inflation,
            "gdp": self.gdp_growth,
            "unemployment": self.unemployment,
            "rate": policy_rate,
            "fx": self.exchange_rate
        })