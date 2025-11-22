import random
import copy

class Government:
    TYPES = {
        "Populist": {
            "name_fa": "دولت پوپولیست (خرج‌کننده)",
            "desc": "تمرکز بر محبوبیت. تورم‌زا. حساسیت شدید به بیکاری.",
            "budget_bias": 1.5, "inflation_bias": 1.0, "tension_speed": 1.5
        },
        "Austerity": {
            "name_fa": "دولت ریاضتی (انضباط مالی)",
            "desc": "تمرکز بر کاهش بدهی. ضدتورم ولی رکودزا.",
            "budget_bias": -0.5, "inflation_bias": -0.5, "tension_speed": 0.8
        },
        "Liberal": {
            "name_fa": "دولت لیبرال (بازار آزاد)",
            "desc": "دخالت کم. حساسیت شدید به نرخ ارز و سرمایه‌گذاری.",
            "budget_bias": 0.2, "inflation_bias": 0.0, "tension_speed": 1.0, "fx_sensitivity": 2.0
        },
        "Welfare": {
            "name_fa": "دولت رفاه (میانه)",
            "desc": "تعادل بین رشد و ثبات. حمایت از اشتغال.",
            "budget_bias": 0.5, "inflation_bias": 0.2, "tension_speed": 1.0
        }
    }

    def __init__(self, type_key=None):
        if type_key and type_key in self.TYPES:
            self.type_key = type_key
        else:
            self.type_key = random.choice(list(self.TYPES.keys()))
        self.profile = self.TYPES[self.type_key]
        self.name = self.profile["name_fa"]

class Economy:
    # --- Constants ---
    TARGET_INFLATION = 3.0
    TARGET_GDP_GROWTH = 3.0
    TARGET_UNEMPLOYMENT = 5.0

    SENSITIVITY_INFLATION = 0.03
    SENSITIVITY_GDP = 0.04
    SENSITIVITY_UNEMPLOYMENT = 0.25 
    GLOBAL_INTEREST_RATE = 2.0
    SENSITIVITY_FX = 0.1          
    PASS_THROUGH_COEF = 0.2       
    SENSITIVITY_MONEY_INFLATION = 0.15
    SENSITIVITY_MONEY_GDP = 0.15
    SENSITIVITY_MONEY_FX = 0.2
    GRAVITY_GDP = 0.3
    GRAVITY_INFLATION = 0.05
    GRAVITY_UNEMPLOYMENT = 0.05
    
    MIN_INFLATION, MAX_INFLATION = -10.0, 200.0
    MIN_UNEMPLOYMENT, MAX_UNEMPLOYMENT = 2.0, 50.0
    MIN_GDP, MAX_GDP = -15.0, 15.0
    MAX_TURNS = 48

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
        
        self.gov = Government()
        
        # --- FIX: Persist Game Over State ---
        self.game_over_status = {
            "is_game_over": False,
            "reason": "",
            "type": "none"
        }

    def _calculate_effective_rate(self):
        rates = self.policy_history[-3:]
        if len(rates) < 3: return rates[-1]
        return (rates[-1] * 0.10) + (rates[-2] * 0.30) + (rates[-3] * 0.60)

    def _process_random_events(self):
        triggered = []
        if random.random() < 0.05:
            triggered.append({"title": "شوک نفتی", "desc": "افزایش جهانی قیمت نفت.", "type": "negative", "impact": {"inflation": 4.0, "gdp": -2.0}})
            self.inflation += 4.0
            self.gdp_growth -= 2.0
        elif random.random() < 0.05:
            triggered.append({"title": "جهش فناوری", "desc": "افزایش بهره‌وری.", "type": "positive", "impact": {"inflation": -1.0, "gdp": 3.0}})
            self.inflation -= 1.0
            self.gdp_growth += 3.0
        if self.inflation > 20.0 and random.random() < 0.20:
             triggered.append({"title": "اعتصاب کارگران", "desc": "اعتراض به گرانی.", "type": "severe", "impact": {"gdp": -3.0, "unemployment": 2.0}})
             self.gdp_growth -= 3.0
             self.unemployment += 2.0
        return triggered

    def _update_political_tension(self, policy_rate):
        tension_change = 0.0
        self.gov_message = "دولت فعلاً سکوت کرده است."
        speed_mod = self.gov.profile["tension_speed"]
        fx_sens_mod = self.gov.profile.get("fx_sensitivity", 1.0)

        if policy_rate > 15.0:
            diff = policy_rate - 15.0
            tension_change += (diff * 0.4)
            if diff > 10: self.gov_message = "هشدار: نرخ بهره بسیار بالاست!"
        if self.unemployment > 10.0:
            diff = self.unemployment - 10.0
            tension_change += (diff * 0.8)
            if diff > 5: self.gov_message = "هشدار: بیکاری بحرانی است."
        if self.fx_change_rate > 5.0:
             tension_change += (3.0 * fx_sens_mod)
             self.gov_message = "هشدار: سقوط ارزش پول ملی!"
        if policy_rate <= 15.0 and self.unemployment <= 10.0 and self.fx_change_rate < 3.0:
            tension_change -= 3.0
            self.gov_message = "دولت رضایت دارد."

        self.political_tension += (tension_change * speed_mod)
        self.political_tension = max(0.0, min(100.0, self.political_tension))
        if self.political_tension > 85.0:
            self.gov_message = "‼️ اولتیماتوم: خطر برکناری!"

    def _get_advisor_report(self, policy_rate):
        advisors = []
        hawk_msg = "وضعیت مطلوب است."
        if self.inflation > 5.0: hawk_msg = "تورم بالاست! نرخ بهره را افزایش دهید."
        if self.inflation > 15.0: hawk_msg = "فاجعه تورمی! سیاست انقباضی شدید لازم است."
        if policy_rate < self.inflation: hawk_msg += " نرخ بهره واقعی منفی است!"
        advisors.append({"name": "شاهین (ضد تورم)", "msg": hawk_msg, "type": "hawk"})

        dove_msg = "بازار کار آرام است."
        if self.unemployment > 8.0: dove_msg = "مردم بیکارند! کمی پول تزریق کنید."
        if self.unemployment > 15.0: dove_msg = "بحران بیکاری! نرخ بهره را کاهش دهید."
        if self.gdp_growth < 0: dove_msg += " در رکود هستیم!"
        advisors.append({"name": "کبوتر (حامی رشد)", "msg": dove_msg, "type": "dove"})

        tech_msg = "شاخص‌ها متعادلند."
        if abs(self.fx_change_rate) > 3.0: tech_msg = "نوسان ارزی شدید است. ثبات را اولویت دهید."
        if self.political_tension > 60.0: tech_msg = "ریسک سیاسی بالاست. مراقب دولت باشید."
        if self.money_supply_index > 120: tech_msg = "حجم نقدینگی خطرناک است."
        advisors.append({"name": "تکنوکرات", "msg": tech_msg, "type": "techno"})
        return advisors

    def next_turn(self, policy_interest_rate: float, money_printer: float = 0.0, is_simulation: bool = False):
        self.policy_history.append(policy_interest_rate)
        if not is_simulation: self._log_history(policy_interest_rate)

        effective_rate = self._calculate_effective_rate()
        self.money_supply_index += money_printer
        
        rate_differential = effective_rate - self.GLOBAL_INTEREST_RATE
        natural_depreciation = (self.inflation - 2.0) * 0.05
        capital_flow_effect = rate_differential * self.SENSITIVITY_FX
        money_supply_shock = money_printer * self.SENSITIVITY_MONEY_FX
        self.fx_change_rate = natural_depreciation - capital_flow_effect + money_supply_shock
        self.exchange_rate = self.exchange_rate * (1 + (self.fx_change_rate / 100.0))
        self.exchange_rate = max(1000.0, self.exchange_rate)

        real_rate_gap = effective_rate - self.inflation
        gov_inflation = self.gov.profile["inflation_bias"]
        inflation_delta = -(real_rate_gap * self.SENSITIVITY_INFLATION)
        import_inflation = self.fx_change_rate * self.PASS_THROUGH_COEF
        monetary_inflation = money_printer * self.SENSITIVITY_MONEY_INFLATION
        inflation_gravity = (self.TARGET_INFLATION - self.inflation) * self.GRAVITY_INFLATION
        self.inflation += (inflation_delta + import_inflation + monetary_inflation + inflation_gravity + gov_inflation)

        gov_spending = self.gov.profile["budget_bias"]
        gdp_pressure = -(real_rate_gap * self.SENSITIVITY_GDP)
        export_boost = self.fx_change_rate * 0.03
        monetary_stimulus = money_printer * self.SENSITIVITY_MONEY_GDP
        gdp_gravity = (self.TARGET_GDP_GROWTH - self.gdp_growth) * self.GRAVITY_GDP
        self.gdp_growth += (gdp_pressure + export_boost + monetary_stimulus + gdp_gravity + gov_spending)

        gdp_gap = self.TARGET_GDP_GROWTH - self.gdp_growth
        unemployment_delta = (gdp_gap * self.SENSITIVITY_UNEMPLOYMENT)
        unemployment_gravity = (self.TARGET_UNEMPLOYMENT - self.unemployment) * self.GRAVITY_UNEMPLOYMENT
        self.unemployment += (unemployment_delta + unemployment_gravity)

        if not is_simulation:
            self.active_events = self._process_random_events()
            self._update_political_tension(policy_interest_rate)
        else:
            self.active_events = []
            self._update_political_tension(policy_interest_rate)

        self.inflation = max(self.MIN_INFLATION, min(self.MAX_INFLATION, self.inflation))
        self.unemployment = max(self.MIN_UNEMPLOYMENT, min(self.MAX_UNEMPLOYMENT, self.unemployment))
        self.gdp_growth = max(self.MIN_GDP, min(self.MAX_GDP, self.gdp_growth))
        self.turn += 1
        
        # --- FIX: Persistent Game Over Logic ---
        if not self.game_over_status["is_game_over"]: # Only check if not already over
            if self.political_tension >= 100.0:
                self.game_over_status = {"is_game_over": True, "type": "lose_pol", "reason": f"شما برکنار شدید! {self.gov.name} دیگر تحمل سیاست‌های شما را نداشت."}
            elif self.inflation >= 100.0:
                self.game_over_status = {"is_game_over": True, "type": "lose_eco", "reason": "فروپاشی اقتصادی! ابرتورم پول ملی را نابود کرد."}
            elif self.unemployment >= 30.0:
                self.game_over_status = {"is_game_over": True, "type": "lose_eco", "reason": "شورش گرسنگان! بیکاری گسترده باعث سقوط نظم اجتماعی شد."}
            elif self.turn > self.MAX_TURNS:
                self.game_over_status = {"is_game_over": True, "type": "win", "reason": "تبریک! دوره ریاست ۴ ساله شما با موفقیت به پایان رسید."}

        advisors = self._get_advisor_report(policy_interest_rate)

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
            "money_supply_index": round(self.money_supply_index, 1),
            "gov_type": self.gov.name,
            "gov_desc": self.gov.profile["desc"],
            # Return persistent status
            "is_game_over": self.game_over_status["is_game_over"],
            "game_over_reason": self.game_over_status["reason"],
            "game_over_type": self.game_over_status["type"],
            "advisors": advisors
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

    def simulate_future(self, policy_rate: float, money_printer: float, months: int = 6):
        sim_economy = Economy()
        sim_economy.inflation = self.inflation
        sim_economy.gdp_growth = self.gdp_growth
        sim_economy.unemployment = self.unemployment
        sim_economy.exchange_rate = self.exchange_rate
        sim_economy.fx_change_rate = self.fx_change_rate
        sim_economy.money_supply_index = self.money_supply_index
        sim_economy.turn = self.turn
        sim_economy.policy_history = self.policy_history[:]
        sim_economy.political_tension = self.political_tension
        # IMPORTANT: Clone the current government type correctly
        sim_economy.gov = Government(self.gov.type_key)
        
        forecast_data = []
        for _ in range(months):
            state = sim_economy.next_turn(policy_rate, money_printer, is_simulation=True)
            forecast_data.append({
                "turn": state["turn"],
                "inflation": state["inflation"],
                "gdp_growth": state["gdp_growth"],
                "unemployment": state["unemployment"]
            })
        return forecast_data