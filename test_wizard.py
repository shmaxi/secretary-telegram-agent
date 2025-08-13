#!/usr/bin/env python3

"""Test that wizard properly asks for OpenAI key"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)

print(f"{Fore.CYAN}Testing Setup Wizard Configuration Detection{Style.RESET_ALL}")
print("="*50)

# Check if .env exists
if os.path.exists('.env'):
    print(f"{Fore.GREEN}✅ .env file exists{Style.RESET_ALL}")
    load_dotenv()
else:
    print(f"{Fore.YELLOW}⚠️  No .env file found{Style.RESET_ALL}")
    print("The wizard will create one and ask for all keys")

# Check environment variables
openai_key = os.getenv('OPENAI_API_KEY')
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')

print(f"\n{Fore.CYAN}Current Configuration:{Style.RESET_ALL}")
print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if telegram_token else '❌ Missing'}")

if not openai_key:
    print(f"\n{Fore.RED}The wizard WILL ask for your OpenAI API key{Style.RESET_ALL}")
if not telegram_token:
    print(f"{Fore.RED}The wizard WILL ask for your Telegram bot token{Style.RESET_ALL}")

if not openai_key or not telegram_token:
    print(f"\n{Fore.YELLOW}Run 'python setup_wizard.py' to configure missing keys{Style.RESET_ALL}")
else:
    print(f"\n{Fore.GREEN}All required keys are configured!{Style.RESET_ALL}")