#!/usr/bin/env python3

"""
Quick script to add OpenAI API key to .env file
"""

import os
import sys
from dotenv import load_dotenv, set_key
from colorama import init, Fore, Style
import getpass

init(autoreset=True)

def main():
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}OpenAI API Key Setup{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    
    # Create .env if it doesn't exist
    if not os.path.exists('.env'):
        open('.env', 'a').close()
        print(f"{Fore.GREEN}Created .env file{Style.RESET_ALL}")
    
    # Check if key already exists
    load_dotenv()
    existing_key = os.getenv('OPENAI_API_KEY')
    
    if existing_key and existing_key != 'test_key_12345':
        print(f"{Fore.YELLOW}OpenAI key already configured!{Style.RESET_ALL}")
        overwrite = input(f"{Fore.YELLOW}Overwrite existing key? (y/n): {Style.RESET_ALL}").lower()
        if overwrite != 'y':
            print("Keeping existing key.")
            return
    
    print(f"\n{Fore.WHITE}Enter your OpenAI API key{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Note: Keys start with 'sk-' and are about 50 characters long{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Get your key at: https://platform.openai.com/api-keys{Style.RESET_ALL}\n")
    
    api_key = getpass.getpass(f"{Fore.GREEN}➤ API Key: {Style.RESET_ALL}")
    
    if not api_key:
        print(f"{Fore.RED}No key entered!{Style.RESET_ALL}")
        sys.exit(1)
    
    if not api_key.startswith('sk-'):
        print(f"{Fore.YELLOW}Warning: Key doesn't start with 'sk-' - might be invalid{Style.RESET_ALL}")
        confirm = input(f"{Fore.YELLOW}Continue anyway? (y/n): {Style.RESET_ALL}").lower()
        if confirm != 'y':
            sys.exit(1)
    
    # Save the key
    set_key('.env', 'OPENAI_API_KEY', api_key)
    print(f"\n{Fore.GREEN}✅ OpenAI API key saved to .env file!{Style.RESET_ALL}")
    
    # Also set model if not set
    if not os.getenv('OPENAI_MODEL_NAME'):
        set_key('.env', 'OPENAI_MODEL_NAME', 'gpt-4o-mini')
        print(f"{Fore.GREEN}✅ Default model set to gpt-4o-mini{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}You can now run: python start.py{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")