import sys
import os
import unittest
import logging

# Setup path to import engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import Economy

# Setup nicer logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("CalibrationLab")

class TestEconomyCalibration(unittest.TestCase):
    
    def print_header(self, title, gov_type):
        logger.info("\n" + "="*120)
        logger.info(f"🧪 SCENARIO: {title.upper()}")
        logger.info(f"🏛️  GOVERNMENT: {gov_type}")
        logger.info("-" * 120)
        logger.info(f"{'Turn':<4} | {'Rate':<5} | {'Print':<5} | {'Infl%':<7} | {'GDP%':<7} | {'Unemp%':<7} | {'FX Rate':<9} | {'FX Chg%':<7} | {'Tension':<7} | {'Status'}")
        logger.info("-" * 120)

    def log_turn(self, state, rate, printer):
        status = "🔴 OVER" if state['is_game_over'] else "🟢 OK"
        logger.info(
            f"{state['turn']:<4} | "
            f"{rate:<5.1f} | "
            f"{printer:<5.1f} | "
            f"{state['inflation']:<7.2f} | "
            f"{state['gdp_growth']:<7.2f} | "
            f"{state['unemployment']:<7.2f} | "
            f"{state['exchange_rate']:<9.0f} | "
            f"{state['fx_change']:<7.2f} | "
            f"{state['political_tension']:<7.1f} | "
            f"{status}"
        )

    def run_simulation(self, title, gov_type, strategy_fn, duration=24, init_infl=15.0):
        self.print_header(title, gov_type)
        game = Economy(fixed_gov_type=gov_type, initial_inflation=init_infl)
        
        for _ in range(duration):
            if game.game_over_status["is_game_over"]:
                break
            
            # Ask strategy function for inputs
            rate, printer = strategy_fn(game)
            state = game.next_turn(rate, printer)
            self.log_turn(state, rate, printer)
            
        return game

    # --- STRATEGIES ---
    
    def strategy_hawk(self, game):
        # Aggressive anti-inflation: Rate = Inflation + 5, Sell Bonds (-5)
        target_rate = game.inflation + 5.0
        return min(40.0, target_rate), -5.0

    def strategy_dove(self, game):
        # Growth focus: Low rate (10%), Print money (+5)
        return 10.0, 5.0

    def strategy_balanced(self, game):
        # Taylor Rule-ish: Rate = Inflation + 2
        return max(5.0, game.inflation + 2.0), 0.0

    def strategy_panic(self, game):
        # Rate 0, Print 20 (Hyperinflation run)
        return 0.0, 20.0

    # --- TESTS ---

    def test_01_austerity_vs_inflation(self):
        """Scenario: Austerity Gov battling 25% inflation."""
        game = self.run_simulation(
            "Fighting High Inflation", 
            "Austerity", 
            self.strategy_hawk, 
            init_infl=25.0
        )
        self.assertLess(game.inflation, 15.0, "Hawk strategy failed to lower inflation")
        self.assertGreater(game.unemployment, 10.0, "Recession didn't hurt employment enough")

    def test_02_populist_spending(self):
        """Scenario: Populist Gov printing money."""
        game = self.run_simulation(
            "Populist Spending Spree", 
            "Populist", 
            self.strategy_dove
        )
        self.assertGreater(game.inflation, 20.0, "Printing money didn't cause inflation")
        self.assertGreater(game.gdp_growth, 3.0, "Stimulus didn't boost GDP")

    def test_03_liberal_fx_crisis(self):
        """Scenario: Liberal Gov watching currency collapse."""
        game = self.run_simulation(
            "Currency Crisis (Panic Mode)", 
            "Liberal", 
            self.strategy_panic,
            duration=12
        )
        self.assertGreater(game.exchange_rate, 60000, "Currency didn't devalue enough")
        self.assertGreater(game.political_tension, 80.0, "Liberal gov should hate FX instability")

    def test_04_welfare_stability(self):
        """Scenario: Welfare Gov trying to be balanced."""
        game = self.run_simulation(
            "Stability Run", 
            "Welfare", 
            self.strategy_balanced,
            duration=36
        )
        self.assertFalse(game.game_over_status["is_game_over"], "Balanced strategy shouldn't lose quickly")
        self.assertTrue(10.0 < game.inflation < 20.0, "Inflation should stabilize")

if __name__ == '__main__':
    unittest.main()