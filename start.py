#!/usr/bin/env python3

"""
Autonomous Virtual Secretary - Main Launcher

This script checks for proper setup and launches the secretary bot.
If setup is incomplete, it runs the setup wizard first.
"""

import os
import sys
import subprocess
from pathlib import Path
from colorama import init, Fore, Style
from dotenv import load_dotenv

init(autoreset=True)

def check_setup():
    """Check if all required configurations are present"""
    load_dotenv()
    
    required = {
        'OPENAI_API_KEY': 'OpenAI API',
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot'
    }
    
    optional = {
        'SERPER_API_KEY': 'Serper API (Weather)',
        'GOOGLE_CREDENTIALS_PATH': 'Google Services'
    }
    
    missing_required = []
    missing_optional = []
    
    for key, name in required.items():
        if not os.getenv(key):
            missing_required.append(name)
    
    for key, name in optional.items():
        if not os.getenv(key):
            missing_optional.append(name)
    
    return missing_required, missing_optional

def print_header():
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🤖 {Style.BRIGHT}AUTONOMOUS VIRTUAL SECRETARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def main():
    print_header()
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print(f"{Fore.YELLOW}No configuration found. Starting setup wizard...{Style.RESET_ALL}\n")
        try:
            subprocess.run([sys.executable, 'setup_wizard.py'], check=True)
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}Setup failed. Please run setup_wizard.py manually.{Style.RESET_ALL}")
            sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Setup cancelled.{Style.RESET_ALL}")
            sys.exit(0)
    
    # Check configuration
    missing_required, missing_optional = check_setup()
    
    if missing_required:
        print(f"{Fore.RED}❌ Missing required configurations:{Style.RESET_ALL}")
        for item in missing_required:
            print(f"   • {item}")
        
        print(f"\n{Fore.YELLOW}Running setup wizard to configure missing items...{Style.RESET_ALL}\n")
        try:
            subprocess.run([sys.executable, 'setup_wizard.py'], check=True)
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}Setup failed. Cannot start bot without required configurations.{Style.RESET_ALL}")
            sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Setup cancelled.{Style.RESET_ALL}")
            sys.exit(0)
        
        # Re-check after setup
        missing_required, missing_optional = check_setup()
        if missing_required:
            print(f"{Fore.RED}Setup incomplete. Cannot start bot.{Style.RESET_ALL}")
            sys.exit(1)
    
    # Show configuration status
    print(f"{Fore.GREEN}✅ Configuration Status:{Style.RESET_ALL}")
    print(f"   • OpenAI API: {Fore.GREEN}Configured{Style.RESET_ALL}")
    print(f"   • Telegram Bot: {Fore.GREEN}Configured{Style.RESET_ALL}")
    
    if missing_optional:
        print(f"\n{Fore.YELLOW}⚠️  Optional features not configured:{Style.RESET_ALL}")
        for item in missing_optional:
            print(f"   • {item}")
        print(f"\n{Fore.WHITE}You can configure these later by running setup_wizard.py{Style.RESET_ALL}")
    else:
        print(f"   • Google Services: {Fore.GREEN}Configured{Style.RESET_ALL}")
        print(f"   • Weather (Serper): {Fore.GREEN}Configured{Style.RESET_ALL}")
    
    # Start the bot
    print(f"\n{Fore.GREEN}🚀 Starting Autonomous Virtual Secretary...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Press Ctrl+C to stop the bot{Style.RESET_ALL}\n")
    
    try:
        subprocess.run([sys.executable, 'autonomous_telegram_bot.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Bot crashed with error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Bot stopped. Goodbye!{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)