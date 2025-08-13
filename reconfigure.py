#!/usr/bin/env python3

"""
Reconfigure existing settings without re-entering API keys
"""

import os
import sys
from dotenv import load_dotenv, set_key
from colorama import init, Fore, Style

init(autoreset=True)

class Reconfigure:
    def __init__(self):
        self.env_file = '.env'
        load_dotenv()
        
    def print_header(self):
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⚙️  {Style.BRIGHT}RECONFIGURE SETTINGS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    def show_current_settings(self):
        print(f"{Fore.YELLOW}Current Settings:{Style.RESET_ALL}")
        print(f"  • Model: {os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')}")
        print(f"  • Thinking Interval: {os.getenv('THINKING_INTERVAL_MINUTES', '3')} minutes")
        print(f"  • Follow-up Timing: {os.getenv('FOLLOWUP_HOURS', '24')} hours")
        print(f"  • Routines: {os.getenv('ENABLE_ROUTINES', 'True')}")
        print(f"  • Learning: {os.getenv('ENABLE_LEARNING', 'True')}")
        print()
    
    def get_input(self, prompt: str) -> str:
        return input(f"{Fore.GREEN}➤ {prompt}: {Style.RESET_ALL}").strip()
    
    def configure_model(self):
        print(f"\n{Fore.CYAN}1. AI Model{Style.RESET_ALL}")
        print("Options: gpt-4o-mini, gpt-4o, gpt-3.5-turbo")
        current = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')
        print(f"Current: {current}")
        
        change = self.get_input("Change model? (y/n)").lower()
        if change == 'y':
            model = self.get_input("Enter model name")
            if model:
                set_key(self.env_file, 'OPENAI_MODEL_NAME', model)
                print(f"{Fore.GREEN}✅ Model updated to {model}{Style.RESET_ALL}")
    
    def configure_interval(self):
        print(f"\n{Fore.CYAN}2. Thinking Interval{Style.RESET_ALL}")
        current = os.getenv('THINKING_INTERVAL_MINUTES', '3')
        print(f"Current: {current} minutes")
        print("Recommended: 1-2 (responsive), 3-5 (balanced), 10-15 (conservative)")
        
        change = self.get_input("Change interval? (y/n)").lower()
        if change == 'y':
            try:
                interval = int(self.get_input("Enter minutes (1-60)"))
                if 1 <= interval <= 60:
                    set_key(self.env_file, 'THINKING_INTERVAL_MINUTES', str(interval))
                    print(f"{Fore.GREEN}✅ Interval updated to {interval} minutes{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid range{Style.RESET_ALL}")
            except:
                print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
    
    def configure_followup(self):
        print(f"\n{Fore.CYAN}3. Follow-up Timing{Style.RESET_ALL}")
        current = os.getenv('FOLLOWUP_HOURS', '24')
        print(f"Current: {current} hours")
        
        change = self.get_input("Change timing? (y/n)").lower()
        if change == 'y':
            try:
                hours = int(self.get_input("Enter hours (1-168)"))
                if 1 <= hours <= 168:
                    set_key(self.env_file, 'FOLLOWUP_HOURS', str(hours))
                    print(f"{Fore.GREEN}✅ Follow-up timing updated to {hours} hours{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid range{Style.RESET_ALL}")
            except:
                print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
    
    def configure_features(self):
        print(f"\n{Fore.CYAN}4. Features{Style.RESET_ALL}")
        
        # Routines
        current_routines = os.getenv('ENABLE_ROUTINES', 'True')
        print(f"\nRoutines currently: {current_routines}")
        change = self.get_input("Toggle routines? (y/n)").lower()
        if change == 'y':
            new_value = 'False' if current_routines == 'True' else 'True'
            set_key(self.env_file, 'ENABLE_ROUTINES', new_value)
            print(f"{Fore.GREEN}✅ Routines {'enabled' if new_value == 'True' else 'disabled'}{Style.RESET_ALL}")
        
        # Learning
        current_learning = os.getenv('ENABLE_LEARNING', 'True')
        print(f"\nLearning currently: {current_learning}")
        change = self.get_input("Toggle learning? (y/n)").lower()
        if change == 'y':
            new_value = 'False' if current_learning == 'True' else 'True'
            set_key(self.env_file, 'ENABLE_LEARNING', new_value)
            print(f"{Fore.GREEN}✅ Learning {'enabled' if new_value == 'True' else 'disabled'}{Style.RESET_ALL}")
    
    def run(self):
        self.print_header()
        
        if not os.path.exists(self.env_file):
            print(f"{Fore.RED}No .env file found!{Style.RESET_ALL}")
            print(f"Run {Fore.YELLOW}python setup_wizard.py{Style.RESET_ALL} first")
            sys.exit(1)
        
        self.show_current_settings()
        
        print(f"{Fore.YELLOW}What would you like to reconfigure?{Style.RESET_ALL}")
        print("1. AI Model")
        print("2. Thinking Interval")
        print("3. Follow-up Timing")
        print("4. Features (Routines/Learning)")
        print("5. All Settings")
        print("6. Exit")
        
        choice = self.get_input("\nSelect option (1-6)")
        
        if choice == '1':
            self.configure_model()
        elif choice == '2':
            self.configure_interval()
        elif choice == '3':
            self.configure_followup()
        elif choice == '4':
            self.configure_features()
        elif choice == '5':
            self.configure_model()
            self.configure_interval()
            self.configure_followup()
            self.configure_features()
        elif choice == '6':
            print(f"{Fore.YELLOW}No changes made{Style.RESET_ALL}")
            return
        else:
            print(f"{Fore.RED}Invalid option{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Settings updated! Restart the bot for changes to take effect.{Style.RESET_ALL}")
        print(f"\nRun: {Fore.YELLOW}python start.py{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        reconfig = Reconfigure()
        reconfig.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")