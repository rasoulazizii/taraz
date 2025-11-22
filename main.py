# main.py
import os
from engine import Economy

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_dashboard(state, last_policy_rate=None):
    print("=" * 50)
    print(f"🗓  Turn (Month): {state['turn']}")
    print("=" * 50)
    print(f"📈 Inflation:        {state['inflation']}%")
    print(f"🏭 GDP Growth:       {state['gdp_growth']}%")
    print(f"👷 Unemployment:     {state['unemployment']}%")
    print("-" * 50)
    
    # Show Policy Context
    if last_policy_rate is not None:
        print(f"🏦 Last Policy Rate: {last_policy_rate}%")
    
    # Show the 'Ghost' rate (Effective Rate) if available
    if 'effective_rate' in state:
        print(f"👻 Effective Rate:   {state['effective_rate']}% (Market Impact)")
        print("   (Note: Policy acts with a 3-month lag)")
    print("=" * 50)

def main():
    game = Economy()
    
    clear_screen()
    print("=== TARAZ: Macro-Economic Simulator (Alpha CLI) ===")
    print("You are the Central Bank Governor.")
    
    # Initial display state
    current_state = {
        "turn": game.turn,
        "inflation": game.inflation,
        "gdp_growth": game.gdp_growth,
        "unemployment": game.unemployment,
        "effective_rate": 15.0 # Initial assumption
    }
    
    last_input_rate = 15.0

    while True:
        print_dashboard(current_state, last_input_rate)
        
        try:
            user_input = input("\n>> Set Policy Interest Rate % (or 'q' to quit): ")
            if user_input.lower() == 'q':
                break
            
            interest_rate = float(user_input)
            last_input_rate = interest_rate
            
            # Process Turn
            current_state = game.next_turn(interest_rate)
            
            clear_screen()
            print(f"✅ Policy Rate set to {interest_rate}%. Simulating market reaction...\n")
            
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()