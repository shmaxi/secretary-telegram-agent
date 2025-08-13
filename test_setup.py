#!/usr/bin/env python3

"""
Test script to verify all components are working
"""

import sys
from colorama import init, Fore, Style

init(autoreset=True)

def test_imports():
    """Test if all required imports work"""
    print(f"{Fore.CYAN}Testing imports...{Style.RESET_ALL}")
    
    tests = []
    
    # Test core dependencies
    try:
        import crewai
        tests.append(("CrewAI", True, None))
    except ImportError as e:
        tests.append(("CrewAI", False, str(e)))
    
    try:
        import telegram
        tests.append(("Python-Telegram-Bot", True, None))
    except ImportError as e:
        tests.append(("Python-Telegram-Bot", False, str(e)))
    
    try:
        from dotenv import load_dotenv
        tests.append(("Python-Dotenv", True, None))
    except ImportError as e:
        tests.append(("Python-Dotenv", False, str(e)))
    
    try:
        import openai
        tests.append(("OpenAI", True, None))
    except ImportError as e:
        tests.append(("OpenAI", False, str(e)))
    
    # Test our modules
    try:
        from autonomous_secretary import AutonomousSecretary
        tests.append(("AutonomousSecretary", True, None))
    except ImportError as e:
        tests.append(("AutonomousSecretary", False, str(e)))
    
    try:
        from autonomous_telegram_bot import AutonomousTelegramBot
        tests.append(("AutonomousTelegramBot", True, None))
    except ImportError as e:
        tests.append(("AutonomousTelegramBot", False, str(e)))
    
    try:
        from memory_store import MemoryStore
        tests.append(("MemoryStore", True, None))
    except ImportError as e:
        tests.append(("MemoryStore", False, str(e)))
    
    # Print results
    print(f"\n{Fore.YELLOW}Import Test Results:{Style.RESET_ALL}")
    all_passed = True
    for name, passed, error in tests:
        if passed:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}: {error}")
            all_passed = False
    
    return all_passed

def test_environment():
    """Test if environment variables are set"""
    print(f"\n{Fore.CYAN}Testing environment configuration...{Style.RESET_ALL}")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    configs = []
    
    # Check required
    openai_key = os.getenv('OPENAI_API_KEY')
    configs.append(("OPENAI_API_KEY", bool(openai_key), True))
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    configs.append(("TELEGRAM_BOT_TOKEN", bool(telegram_token), True))
    
    # Check optional
    serper_key = os.getenv('SERPER_API_KEY')
    configs.append(("SERPER_API_KEY", bool(serper_key), False))
    
    google_creds = os.getenv('GOOGLE_CREDENTIALS_PATH')
    configs.append(("GOOGLE_CREDENTIALS_PATH", bool(google_creds), False))
    
    # Print results
    print(f"\n{Fore.YELLOW}Environment Configuration:{Style.RESET_ALL}")
    all_required_set = True
    for name, is_set, required in configs:
        status = "✅" if is_set else ("❌" if required else "⚠️")
        req_text = " (Required)" if required else " (Optional)"
        print(f"  {status} {name}{req_text}")
        if required and not is_set:
            all_required_set = False
    
    return all_required_set

def main():
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔧 Virtual Secretary Setup Test{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    
    # Run tests
    imports_ok = test_imports()
    env_ok = test_environment()
    
    # Summary
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
    
    if imports_ok and env_ok:
        print(f"{Fore.GREEN}✅ All tests passed! Your setup is ready.{Style.RESET_ALL}")
        print(f"\nYou can now run: {Fore.YELLOW}python start.py{Style.RESET_ALL}")
        return 0
    elif imports_ok and not env_ok:
        print(f"{Fore.YELLOW}⚠️  Imports OK but configuration needed.{Style.RESET_ALL}")
        print(f"\nRun: {Fore.YELLOW}python setup_wizard.py{Style.RESET_ALL}")
        return 1
    else:
        print(f"{Fore.RED}❌ Setup incomplete. Please check errors above.{Style.RESET_ALL}")
        if not imports_ok:
            print(f"\nRun: {Fore.YELLOW}pip install -r requirements.txt{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())