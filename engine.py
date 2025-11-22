# engine.py

class Economy:
    def __init__(self):
        # مقادیر اولیه (بر اساس یک اقتصاد نرمال)
        self.inflation = 15.0      # درصد (تورم)
        self.gdp_growth = 2.0      # درصد (رشد اقتصادی)
        self.unemployment = 10.0   # درصد (بیکاری)
        
        # وضعیت جاری (Turn)
        self.turn = 1
        
        # تاریخچه برای دیباگ (فعلا ساده)
        self.history = []

    def next_turn(self, policy_interest_rate: float):
        """
        محاسبه وضعیت ماه بعد بر اساس نرخ بهره ورودی
        policy_interest_rate: عدد درصد (مثلا 18.0 برای 18 درصد)
        """
        # ذخیره وضعیت قبل از تغییر
        self._log_history(policy_interest_rate)

        # --- منطق ساده شده (Placeholder Logic) ---
        # محاسبه نرخ بهره واقعی (Real Interest Rate)
        # اگر بهره > تورم باشد، سیاست انقباضی است (ضد تورم، ضد رشد)
        real_rate_gap = policy_interest_rate - self.inflation

        # 1. اثر روی تورم
        # اگر بهره بالا باشد، تورم کم می‌شود
        # ضریب 0.2: حساسیت تورم به نرخ بهره
        inflation_change = -(real_rate_gap * 0.2)
        self.inflation += inflation_change

        # 2. اثر روی رشد اقتصادی
        # رابطه معکوس با نرخ بهره واقعی
        # ضریب 0.1: حساسیت تولید به نرخ بهره
        gdp_change = -(real_rate_gap * 0.1)
        self.gdp_growth += gdp_change

        # 3. اثر روی بیکاری (قانون اوکان معکوس)
        # اگر رشد کم شود، بیکاری زیاد می‌شود
        # ضریب -0.5: هر 1 درصد کاهش رشد، 0.5 درصد بیکاری اضافه می‌کند
        unemployment_change = -(gdp_change * 0.5)
        self.unemployment += unemployment_change

        # نرمال‌سازی اعداد (نمی‌گذاریم منفی‌های عجیب شوند فعلا)
        self.inflation = max(-5.0, self.inflation)
        self.unemployment = max(0.0, self.unemployment)

        # رفتن به ماه بعد
        self.turn += 1

        return {
            "turn": self.turn,
            "inflation": round(self.inflation, 2),
            "gdp_growth": round(self.gdp_growth, 2),
            "unemployment": round(self.unemployment, 2)
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