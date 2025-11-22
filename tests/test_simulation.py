# tests/test_simulation.py
import sys
import os
import unittest

# Add parent directory to path so we can import engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import Economy

class TestEconomySimulation(unittest.TestCase):
    
    def test_scenario_high_interest_rate(self):
        """
        Scenario: Governor sets rate to 30% (Very High).
        Expectation: Inflation drops significantly, Unemployment rises.
        """
        print("\n--- Testing High Interest Rate (Contraction) ---")
        game = Economy()
        
        # Initial Inflation is 15.0
        # Apply 30% rate for 10 months
        for _ in range(10):
            state = game.next_turn(30.0)
            
        print(f"Final State after 10 turns: {state}")
        
        # Assertions
        self.assertLess(state['inflation'], 15.0, "Inflation should drop with high rates")
        self.assertGreater(state['unemployment'], 10.0, "Unemployment should rise with high rates")

    def test_scenario_low_interest_rate(self):
        """
        Scenario: Governor sets rate to 0% (Very Low).
        Expectation: Inflation skyrockets, GDP booms.
        """
        print("\n--- Testing Low Interest Rate (Expansion) ---")
        game = Economy()
        
        # Apply 0% rate for 10 months
        for _ in range(10):
            state = game.next_turn(0.0)
            
        print(f"Final State after 10 turns: {state}")
        
        self.assertGreater(state['inflation'], 15.0, "Inflation should rise with low rates")
        self.assertGreater(state['gdp_growth'], 2.0, "GDP should grow with cheap money")

    def test_stability_check(self):
        """
        Scenario: Extreme check. Run for 50 turns.
        Ensure variables don't become NaN or Infinity.
        """
        print("\n--- Testing Long Term Stability ---")
        game = Economy()
        for _ in range(50):
            game.next_turn(15.0) # Neutral rate
        
        self.assertTrue(-10 < game.gdp_growth < 20, "GDP growth stayed within sane limits")

if __name__ == '__main__':
    unittest.main()