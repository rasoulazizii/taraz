# main.py
import os
from engine import Economy

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_dashboard(state):
    print("-" * 40)
    print(f"🗓  ماه (Turn): {state['turn']}")
    print("-" * 40)
    print(f"📈 تورم:        {state['inflation']}%")
    print(f"🏭 رشد تولید:   {state['gdp_growth']}%")
    print(f"👷 بیکاری:      {state['unemployment']}%")
    print("-" * 40)

def main():
    # راه‌اندازی هسته بازی
    game = Economy()
    
    clear_screen()
    print("=== شبیه‌ساز اقتصاد کلان: تراز (نسخه آلفا) ===")
    print("شما رئیس بانک مرکزی هستید.")
    
    current_state = {
        "turn": game.turn,
        "inflation": game.inflation,
        "gdp_growth": game.gdp_growth,
        "unemployment": game.unemployment
    }

    while True:
        print_dashboard(current_state)
        
        try:
            user_input = input("\n>> نرخ بهره جدید را وارد کنید (یا 'q' برای خروج): ")
            if user_input.lower() == 'q':
                break
            
            interest_rate = float(user_input)
            
            # اجرای نوبت بعدی
            current_state = game.next_turn(interest_rate)
            
            clear_screen()
            print(f"✅ نرخ بهره {interest_rate}% اعمال شد.\n")
            
        except ValueError:
            print("❌ لطفا یک عدد معتبر وارد کنید.")

if __name__ == "__main__":
    main()