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
        self.active_events = []

        # --- New: Political State ---
        self.political_tension = 0.0  # 0 to 100
        self.gov_message = "دولت فعلاً سکوت کرده است."

    def _calculate_effective_rate(self):
        rates = self.policy_history[-3:]
        if len(rates) < 3:
            return rates[-1]
        return (rates[-1] * 0.10) + (rates[-2] * 0.30) + (rates[-3] * 0.60)

    def _process_random_events(self):
        triggered = []
        # (Event logic remains same as previous step, removed logs to keep clean)
        # 1. Oil Shock (5%)
        if random.random() < 0.05:
            triggered.append({
                "title": "شوک نفتی", "desc": "قیمت جهانی نفت افزایش یافت.", "type": "negative",
                "impact": {"inflation": 4.0, "gdp": -2.0}
            })
            self.inflation += 4.0
            self.gdp_growth -= 2.0
        # 2. Tech Boom (5%)
        elif random.random() < 0.05:
            triggered.append({
                "title": "جهش فناوری", "desc": "بهره‌وری افزایش یافت.", "type": "positive",
                "impact": {"inflation": -1.0, "gdp": 3.0}
            })
            self.inflation -= 1.0
            self.gdp_growth += 3.0
        # 3. Strike (Conditional)
        if self.inflation > 20.0 and random.random() < 0.20:
             triggered.append({
                "title": "اعتصاب کارگران", "desc": "اعتراض به گرانی.", "type": "severe",
                "impact": {"gdp": -3.0, "unemployment": 2.0}
            })
             self.gdp_growth -= 3.0
             self.unemployment += 2.0
        return triggered

    def _update_political_tension(self, policy_rate):
        """
        Government hates high interest rates and high unemployment.
        """
        tension_change = 0.0
        self.gov_message = "دولت وضعیت را رصد می‌کند."

        # 1. Friction from High Interest Rates (Govt wants cheap debt)
        # If rate > 12%, tension rises.
        if policy_rate > 12.0:
            diff = policy_rate - 12.0
            tension_change += (diff * 0.5) # +0.5 tension per 1% excess rate
            if diff > 10:
                self.gov_message = "هشدار دولت: نرخ بهره بسیار بالاست! هزینه بدهی‌ها کمرشکن شده."

        # 2. Friction from Unemployment (Govt wants votes)
        # If unemployment > 8%, tension rises quickly.
        if self.unemployment > 8.0:
            diff = self.unemployment - 8.0
            tension_change += (diff * 0.8)
            if diff > 5:
                self.gov_message = "هشدار دولت: بیکاری بحرانی است. مردم عصبانی هستند!"

        # 3. Relief (Decay)
        # If things are okay, tension drops slowly
        if policy_rate <= 12.0 and self.unemployment <= 8.0:
            tension_change -= 2.0
            self.gov_message = "دولت از عملکرد شما رضایت نسبی دارد."

        # Apply Change
        self.political_tension += tension_change
        
        # Clamp (0 to 100)
        self.political_tension = max(0.0, min(100.0, self.political_tension))
        
        # Critical Message
        if self.political_tension > 80.0:
            self.gov_message = "‼️ اولتیماتوم: استقلال بانک مرکزی در خطر است! رویه را تغییر دهید."

    def next_turn(self, policy_interest_rate: float):
        self.policy_history.append(policy_interest_rate)
        self._log_history(policy_interest_rate)

        effective_rate = self._calculate_effective_rate()
        real_rate_gap = effective_rate - self.inflation

        # Core Physics (Same as before)
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

        # Process Events
        self.active_events = self._process_random_events()

        # --- New: Update Politics ---
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
            "political_tension": round(self.political_tension, 1), # New
            "gov_message": self.gov_message # New
        }

    def _log_history(self, policy_rate):
        self.history.append({
            "turn": self.turn,
            "inflation": self.inflation,
            "gdp": self.gdp_growth,
            "unemployment": self.unemployment,
            "rate": policy_rate
        })