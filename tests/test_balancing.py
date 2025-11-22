import sys
import os
import unittest
import logging

# افزودن مسیر اصلی پروژه برای ایمپورت کردن engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import Economy

# تنظیمات لاگ‌برداری برای نمایش تمیز در ترمینال
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("BalanceTester")

class TestEconomyBalancing(unittest.TestCase):
    
    def setUp(self):
        self.game = Economy()
        print("\n" + "="*100)

    def print_header(self, scenario_name):
        logger.info(f"\n>>> SCENARIO: {scenario_name}")
        logger.info("-" * 115)
        logger.info(f"{'Turn':<5} | {'Rate':<6} | {'Print':<6} | {'Infl%':<8} | {'GDP%':<8} | {'Unemp%':<8} | {'FX Rate':<10} | {'FX Chg%':<8} | {'Tension':<8}")
        logger.info("-" * 115)

    def log_state(self, state, policy_rate, money_printer):
        """چاپ وضعیت فعلی به صورت یک ردیف در جدول"""
        logger.info(
            f"{state['turn']:<5} | "
            f"{policy_rate:<6.1f} | "
            f"{money_printer:<6.1f} | "
            f"{state['inflation']:<8.2f} | "
            f"{state['gdp_growth']:<8.2f} | "
            f"{state['unemployment']:<8.2f} | "
            f"{state['exchange_rate']:<10.0f} | "
            f"{state['fx_change']:<8.2f} | "
            f"{state['political_tension']:<8.1f}"
        )

    def test_01_full_contraction(self):
        """
        سناریوی ۱: سیاست انقباضی شدید (ضد تورم)
        - نرخ بهره بالا (25%)
        - جمع‌آوری نقدینگی/فروش اوراق (Printer = -10)
        
        انتظار:
        1. تورم باید به شدت کاهش یابد.
        2. دلار (FX) باید ارزان شود (ریال تقویت شود).
        3. بیکاری باید بالا برود (هزینه رکود).
        4. تنش سیاسی باید قرمز شود.
        """
        self.print_header("Full Contraction (High Rate + QT)")
        
        policy_rate = 25.0
        money_printer = -10.0

        for _ in range(12): # یک سال اجرا
            state = self.game.next_turn(policy_rate, money_printer)
            self.log_state(state, policy_rate, money_printer)

        # تحلیل نتایج (Assertions)
        self.assertLess(self.game.inflation, 15.0, "Inflation did not drop despite severe contraction")
        self.assertLess(self.game.exchange_rate, 50000, "Currency did not appreciate despite high rates")
        self.assertGreater(self.game.unemployment, 10.0, "Unemployment did not rise despite recession")
        self.assertGreater(self.game.political_tension, 20.0, "Government should be angry about high rates")

    def test_02_full_expansion(self):
        """
        سناریوی ۲: سیاست انبساطی شدید (رشد به هر قیمتی)
        - نرخ بهره پایین (5%)
        - چاپ پول (Printer = +10)
        
        انتظار:
        1. تورم منفجر شود.
        2. دلار (FX) گران شود (سقوط ریال).
        3. بیکاری کم شود.
        4. GDP رشد کند.
        """
        self.print_header("Full Expansion (Low Rate + QE)")
        
        policy_rate = 5.0
        money_printer = 10.0

        for _ in range(12):
            state = self.game.next_turn(policy_rate, money_printer)
            self.log_state(state, policy_rate, money_printer)

        # تحلیل نتایج
        self.assertGreater(self.game.inflation, 15.0, "Inflation should rise with money printing")
        self.assertGreater(self.game.exchange_rate, 50000, "Currency should devalue with low rates")
        self.assertGreater(self.game.gdp_growth, 2.0, "GDP should boom with stimulus")

    def test_03_stagflation_survival(self):
        """
        سناریوی ۳: مدیریت بحران (رکود تورمی)
        - وضعیت اولیه: یک شوک نفتی دستی وارد می‌کنیم.
        - استراتژی بازیکن: تلاش برای تعادل (نرخ بهره متوسط 18%، بدون چاپ پول).
        
        هدف: ببینیم آیا اقتصاد با "نیروی جاذبه" (Gravity) خودش را ترمیم می‌کند؟
        """
        self.print_header("Shock Recovery (Oil Crisis -> Stabilization)")
        
        # 1. ایجاد شوک دستی
        print(">>> INJECTING OIL SHOCK...")
        self.game.inflation += 10.0
        self.game.gdp_growth -= 5.0
        self.game.exchange_rate += 10000 # شوک ارزی
        
        policy_rate = 18.0 # نرخ بهره کمی بالاتر از نرمال برای کنترل تورم
        money_printer = 0.0

        for _ in range(24): # دو سال مدیریت
            state = self.game.next_turn(policy_rate, money_printer)
            self.log_state(state, policy_rate, money_printer)

        # بررسی اینکه آیا اقتصاد به تعادل برگشته؟
        self.assertLess(self.game.inflation, 20.0, "Inflation stuck high after shock")
        self.assertGreater(self.game.gdp_growth, 0.0, "Economy failed to exit recession")

    def test_04_political_limit(self):
        """
        سناریوی ۴: تست آستانه تحمل دولت
        - نرخ بهره را وحشتناک بالا می‌بریم (40%)
        - ببینیم کی تنش به 100 می‌رسد؟
        """
        self.print_header("Political Stress Test")
        
        policy_rate = 40.0
        money_printer = 0.0
        
        reached_limit = False
        for i in range(20):
            state = self.game.next_turn(policy_rate, money_printer)
            self.log_state(state, policy_rate, money_printer)
            
            if state['political_tension'] >= 100.0:
                print(f">>> Government patience ended at turn {state['turn']}")
                reached_limit = True
                break
        
        self.assertTrue(reached_limit, "Political tension never reached 100 despite 40% interest rate")

if __name__ == '__main__':
    unittest.main()