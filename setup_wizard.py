#!/usr/bin/env python3

import os
import sys
import json
import time
import webbrowser
import subprocess
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple
from colorama import init, Fore, Style, Back
from dotenv import load_dotenv, set_key

init(autoreset=True)

class SetupWizard:
    def __init__(self):
        self.env_file = '.env'
        self.credentials_file = 'credentials.json'
        self.setup_complete = False
        self.config = {
            'openai': False,
            'telegram': False,
            'google': False,
            'serper': False,
            'advanced': False
        }
        self.advanced_settings = {
            'thinking_interval': 3,
            'followup_hours': 24,
            'model_name': 'gpt-4o-mini',
            'enable_routines': True,
            'enable_learning': True
        }
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🤖 {Style.BRIGHT}AUTONOMOUS VIRTUAL SECRETARY - SETUP WIZARD{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_progress(self):
        print(f"\n{Fore.YELLOW}📊 Setup Progress:{Style.RESET_ALL}")
        print(f"  {'✅' if self.config['openai'] else '❌'} OpenAI API")
        print(f"  {'✅' if self.config['telegram'] else '❌'} Telegram Bot")
        print(f"  {'✅' if self.config['google'] else '⚠️'} Google Services (Optional)")
        print(f"  {'✅' if self.config['serper'] else '⚠️'} Serper API (Optional)")
        print(f"  {'✅' if self.config['advanced'] else '⚠️'} Advanced Settings (Optional)")
        print()
    
    def print_section(self, title: str, icon: str = "📌"):
        print(f"\n{Fore.GREEN}{icon} {Style.BRIGHT}{title}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'-'*50}{Style.RESET_ALL}")
    
    def get_input(self, prompt: str, secret: bool = False) -> str:
        if secret:
            import getpass
            return getpass.getpass(f"{Fore.YELLOW}➤ {prompt}: {Style.RESET_ALL}")
        return input(f"{Fore.YELLOW}➤ {prompt}: {Style.RESET_ALL}").strip()
    
    def validate_openai_key(self, api_key: str) -> Tuple[bool, str]:
        """Validate OpenAI API key by making a test request"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, "Valid API key"
            elif response.status_code == 401:
                return False, "Invalid API key - authentication failed"
            elif response.status_code == 429:
                return False, "Rate limit exceeded - key might be valid but over quota"
            else:
                return False, f"Unexpected status code: {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Connection timeout - check your internet connection"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def validate_telegram_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Validate Telegram bot token and get bot info"""
        try:
            response = requests.get(
                f'https://api.telegram.org/bot{token}/getMe',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return True, bot_info.get('username')
            return False, None
        except:
            return False, None
    
    def validate_serper_key(self, api_key: str) -> bool:
        """Validate Serper API key"""
        try:
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            data = {'q': 'test'}
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def setup_openai(self):
        self.print_section("OPENAI API SETUP", "🔑")
        
        print(f"{Fore.WHITE}OpenAI API is {Fore.RED}REQUIRED{Fore.WHITE} for the AI intelligence.{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Steps to get your API key:{Style.RESET_ALL}")
        print("1. Go to https://platform.openai.com/signup")
        print("2. Sign up or log in")
        print("3. Go to API Keys section")
        print("4. Create new secret key")
        print("5. Copy the key (it won't be shown again!)")
        
        print(f"\n{Fore.YELLOW}Note: Keys start with 'sk-' and are about 50 characters long{Style.RESET_ALL}")
        
        open_browser = self.get_input("\nOpen OpenAI website now? (y/n)").lower()
        if open_browser == 'y':
            webbrowser.open('https://platform.openai.com/api-keys')
            time.sleep(2)
        
        while True:
            api_key = self.get_input("\nEnter your OpenAI API key", secret=True)
            
            if not api_key:
                print(f"{Fore.RED}API key cannot be empty!{Style.RESET_ALL}")
                continue
            
            print(f"{Fore.CYAN}Validating API key...{Style.RESET_ALL}")
            is_valid, message = self.validate_openai_key(api_key)
            
            if is_valid:
                # Save the key immediately
                set_key(self.env_file, 'OPENAI_API_KEY', api_key)
                print(f"{Fore.GREEN}✅ OpenAI API key validated and saved!{Style.RESET_ALL}")
                
                # Verify it was saved
                with open(self.env_file, 'r') as f:
                    if api_key in f.read():
                        print(f"{Fore.GREEN}✅ Confirmed: Key saved to .env file{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️  Warning: Key might not have saved properly{Style.RESET_ALL}")
                
                self.config['openai'] = True
                break
            else:
                print(f"{Fore.RED}❌ Validation failed: {message}{Style.RESET_ALL}")
                
                # Offer to save anyway
                if "timeout" in message.lower() or "connection" in message.lower():
                    save_anyway = self.get_input("Save key anyway? (if you're sure it's correct) (y/n)").lower()
                    if save_anyway == 'y':
                        set_key(self.env_file, 'OPENAI_API_KEY', api_key)
                        print(f"{Fore.YELLOW}⚠️  Key saved without validation{Style.RESET_ALL}")
                        self.config['openai'] = True
                        break
                
                retry = self.get_input("Try again? (y/n)").lower()
                if retry != 'y':
                    print(f"{Fore.RED}OpenAI setup incomplete. The bot won't work without it.{Style.RESET_ALL}")
                    sys.exit(1)
    
    def setup_telegram(self):
        self.print_section("TELEGRAM BOT SETUP", "💬")
        
        print(f"{Fore.WHITE}Telegram Bot Token is {Fore.RED}REQUIRED{Fore.WHITE} for the messaging interface.{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Steps to create your bot:{Style.RESET_ALL}")
        print("1. Open Telegram and search for @BotFather")
        print("2. Start a chat and send: /newbot")
        print("3. Choose a name for your bot (e.g., 'My Secretary')")
        print("4. Choose a username (must end with 'bot', e.g., 'my_secretary_bot')")
        print("5. Copy the token BotFather gives you")
        
        print(f"\n{Fore.YELLOW}💡 Tip: Keep Telegram open on your phone/desktop{Style.RESET_ALL}")
        
        open_telegram = self.get_input("\nOpen Telegram Web now? (y/n)").lower()
        if open_telegram == 'y':
            webbrowser.open('https://web.telegram.org')
            time.sleep(2)
        
        while True:
            token = self.get_input("\nEnter your Telegram Bot Token", secret=True)
            
            if not token:
                print(f"{Fore.RED}Token cannot be empty!{Style.RESET_ALL}")
                continue
            
            print(f"{Fore.CYAN}Validating bot token...{Style.RESET_ALL}")
            valid, bot_username = self.validate_telegram_token(token)
            
            if valid:
                set_key(self.env_file, 'TELEGRAM_BOT_TOKEN', token)
                print(f"{Fore.GREEN}✅ Telegram bot validated and saved!{Style.RESET_ALL}")
                if bot_username:
                    print(f"{Fore.GREEN}📱 Your bot: @{bot_username}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}➤ Start a chat with your bot: https://t.me/{bot_username}{Style.RESET_ALL}")
                self.config['telegram'] = True
                break
            else:
                print(f"{Fore.RED}❌ Invalid token! Make sure you copied it correctly from BotFather.{Style.RESET_ALL}")
                retry = self.get_input("Try again? (y/n)").lower()
                if retry != 'y':
                    print(f"{Fore.RED}Telegram setup incomplete. The bot won't work without it.{Style.RESET_ALL}")
                    sys.exit(1)
    
    def setup_google(self):
        self.print_section("GOOGLE SERVICES SETUP (Optional)", "📧")
        
        print(f"{Fore.WHITE}Google services enable Gmail and Calendar features.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  This is optional but recommended for full functionality.{Style.RESET_ALL}")
        
        setup_google = self.get_input("\nSet up Google services? (y/n)").lower()
        if setup_google != 'y':
            print(f"{Fore.YELLOW}Skipping Google setup. You can set it up later if needed.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Google Cloud Setup Steps:{Style.RESET_ALL}")
        print("1. Go to Google Cloud Console")
        print("2. Create a new project (or select existing)")
        print("3. Enable Gmail API and Google Calendar API")
        print("4. Create credentials (OAuth 2.0 Client ID)")
        print("5. Download credentials as JSON")
        
        print(f"\n{Fore.YELLOW}Detailed Steps:{Style.RESET_ALL}")
        
        steps = [
            ("Open Google Cloud Console", "https://console.cloud.google.com"),
            ("Go to APIs & Services > Library", None),
            ("Search and enable 'Gmail API'", None),
            ("Search and enable 'Google Calendar API'", None),
            ("Go to APIs & Services > Credentials", None),
            ("Click 'Create Credentials' > 'OAuth client ID'", None),
            ("Select 'Desktop app' as application type", None),
            ("Download the credentials JSON file", None),
        ]
        
        for i, (step, url) in enumerate(steps, 1):
            print(f"{i}. {step}")
            if url and i == 1:
                open_url = self.get_input(f"   Open this URL? (y/n)").lower()
                if open_url == 'y':
                    webbrowser.open(url)
        
        print(f"\n{Fore.YELLOW}After downloading the credentials JSON:{Style.RESET_ALL}")
        print(f"Save it as '{self.credentials_file}' in the project directory")
        
        while True:
            creds_path = self.get_input(f"\nEnter path to credentials JSON (or 'skip' to setup later)")
            
            if creds_path.lower() == 'skip':
                print(f"{Fore.YELLOW}Google setup skipped. Gmail/Calendar features won't be available.{Style.RESET_ALL}")
                break
            
            if os.path.exists(creds_path):
                try:
                    with open(creds_path, 'r') as f:
                        creds_data = json.load(f)
                    
                    # Validate it's a proper credentials file
                    if 'installed' in creds_data or 'web' in creds_data:
                        # Copy to project directory
                        with open(self.credentials_file, 'w') as f:
                            json.dump(creds_data, f, indent=2)
                        
                        set_key(self.env_file, 'GOOGLE_CREDENTIALS_PATH', self.credentials_file)
                        print(f"{Fore.GREEN}✅ Google credentials saved!{Style.RESET_ALL}")
                        self.config['google'] = True
                        break
                    else:
                        print(f"{Fore.RED}Invalid credentials file format!{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error reading credentials file: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}File not found: {creds_path}{Style.RESET_ALL}")
    
    def setup_serper(self):
        self.print_section("SERPER API SETUP (Optional)", "🌤️")
        
        print(f"{Fore.WHITE}Serper API enables weather and web search features.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  This is optional. Skip if you don't need weather updates.{Style.RESET_ALL}")
        
        setup_serper = self.get_input("\nSet up Serper API? (y/n)").lower()
        if setup_serper != 'y':
            print(f"{Fore.YELLOW}Skipping Serper setup. Weather features won't be available.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Steps to get Serper API key:{Style.RESET_ALL}")
        print("1. Go to https://serper.dev")
        print("2. Sign up for free account")
        print("3. Get your API key from dashboard")
        print("4. Free tier includes 2,500 queries/month")
        
        open_browser = self.get_input("\nOpen Serper website now? (y/n)").lower()
        if open_browser == 'y':
            webbrowser.open('https://serper.dev')
            time.sleep(2)
        
        while True:
            api_key = self.get_input("\nEnter your Serper API key (or 'skip')", secret=True)
            
            if api_key.lower() == 'skip':
                print(f"{Fore.YELLOW}Serper setup skipped. Weather features won't be available.{Style.RESET_ALL}")
                break
            
            if not api_key:
                print(f"{Fore.RED}API key cannot be empty!{Style.RESET_ALL}")
                continue
            
            print(f"{Fore.CYAN}Validating API key...{Style.RESET_ALL}")
            if self.validate_serper_key(api_key):
                set_key(self.env_file, 'SERPER_API_KEY', api_key)
                print(f"{Fore.GREEN}✅ Serper API key validated and saved!{Style.RESET_ALL}")
                self.config['serper'] = True
                break
            else:
                print(f"{Fore.RED}❌ Invalid API key! Please check and try again.{Style.RESET_ALL}")
                retry = self.get_input("Try again? (y/n)").lower()
                if retry != 'y':
                    break
    
    def setup_advanced(self):
        """Configure advanced settings"""
        self.print_section("ADVANCED SETTINGS", "⚙️")
        
        print(f"{Fore.WHITE}Configure advanced bot behavior and settings.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You can skip this section to use defaults.{Style.RESET_ALL}")
        
        configure = self.get_input("\nConfigure advanced settings? (y/n)").lower()
        if configure != 'y':
            print(f"{Fore.YELLOW}Using default settings.{Style.RESET_ALL}")
            # Save defaults
            self._save_advanced_settings()
            return
        
        # 1. Model Selection
        print(f"\n{Fore.CYAN}1. AI Model Selection{Style.RESET_ALL}")
        print(f"Current default: {self.advanced_settings['model_name']}")
        print("Available options:")
        print("  • gpt-4o-mini (Fast & affordable)")
        print("  • gpt-4o (Most capable)")
        print("  • gpt-3.5-turbo (Fastest)")
        
        change_model = self.get_input("\nChange model? (y/n)").lower()
        if change_model == 'y':
            model = self.get_input("Enter model name")
            if model:
                self.advanced_settings['model_name'] = model
        
        # 2. Thinking Interval
        print(f"\n{Fore.CYAN}2. Autonomous Thinking Interval{Style.RESET_ALL}")
        print(f"How often should the bot check for tasks and make decisions?")
        print(f"Current default: {self.advanced_settings['thinking_interval']} minutes")
        print("Recommendations:")
        print("  • 1-2 minutes: Very responsive (higher API usage)")
        print("  • 3-5 minutes: Balanced (recommended)")
        print("  • 10-15 minutes: Conservative")
        
        change_interval = self.get_input("\nChange interval? (y/n)").lower()
        if change_interval == 'y':
            try:
                interval = int(self.get_input("Enter interval in minutes (1-60)"))
                if 1 <= interval <= 60:
                    self.advanced_settings['thinking_interval'] = interval
                else:
                    print(f"{Fore.YELLOW}Invalid interval. Using default.{Style.RESET_ALL}")
            except:
                print(f"{Fore.YELLOW}Invalid input. Using default.{Style.RESET_ALL}")
        
        # 3. Follow-up Timing
        print(f"\n{Fore.CYAN}3. Email Follow-up Timing{Style.RESET_ALL}")
        print(f"After how many hours should the bot send follow-up reminders?")
        print(f"Current default: {self.advanced_settings['followup_hours']} hours")
        
        change_followup = self.get_input("\nChange follow-up timing? (y/n)").lower()
        if change_followup == 'y':
            try:
                hours = int(self.get_input("Enter hours (1-168)"))
                if 1 <= hours <= 168:
                    self.advanced_settings['followup_hours'] = hours
                else:
                    print(f"{Fore.YELLOW}Invalid hours. Using default.{Style.RESET_ALL}")
            except:
                print(f"{Fore.YELLOW}Invalid input. Using default.{Style.RESET_ALL}")
        
        # 4. Features Toggle
        print(f"\n{Fore.CYAN}4. Feature Settings{Style.RESET_ALL}")
        
        # Routines
        print(f"\nEnable automated routines? (Currently: {self.advanced_settings['enable_routines']})")
        routines = self.get_input("Enable routines? (y/n)").lower()
        self.advanced_settings['enable_routines'] = routines == 'y'
        
        # Learning
        print(f"\nEnable pattern learning? (Currently: {self.advanced_settings['enable_learning']})")
        learning = self.get_input("Enable learning? (y/n)").lower()
        self.advanced_settings['enable_learning'] = learning == 'y'
        
        # Save all advanced settings
        self._save_advanced_settings()
        self.config['advanced'] = True
        
        print(f"\n{Fore.GREEN}✅ Advanced settings configured!{Style.RESET_ALL}")
    
    def _save_advanced_settings(self):
        """Save advanced settings to .env file"""
        set_key(self.env_file, 'OPENAI_MODEL_NAME', self.advanced_settings['model_name'])
        set_key(self.env_file, 'THINKING_INTERVAL_MINUTES', str(self.advanced_settings['thinking_interval']))
        set_key(self.env_file, 'FOLLOWUP_HOURS', str(self.advanced_settings['followup_hours']))
        set_key(self.env_file, 'ENABLE_ROUTINES', str(self.advanced_settings['enable_routines']))
        set_key(self.env_file, 'ENABLE_LEARNING', str(self.advanced_settings['enable_learning']))
    
    def create_env_file(self):
        """Create .env file if it doesn't exist"""
        if not os.path.exists(self.env_file):
            Path(self.env_file).touch()
            print(f"{Fore.GREEN}Created .env file{Style.RESET_ALL}")
    
    def check_existing_setup(self):
        """Check if setup was already completed"""
        if os.path.exists(self.env_file):
            # Force reload of .env file
            load_dotenv(override=True)
            
            openai_key = os.getenv('OPENAI_API_KEY')
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            google_creds = os.getenv('GOOGLE_CREDENTIALS_PATH')
            serper_key = os.getenv('SERPER_API_KEY')
            
            if openai_key and openai_key != 'test_key_12345':  # Ignore test key
                self.config['openai'] = True
            if telegram_token:
                self.config['telegram'] = True
            if google_creds:
                self.config['google'] = True
            if serper_key:
                self.config['serper'] = True
            
            # Load advanced settings if they exist
            if os.getenv('THINKING_INTERVAL_MINUTES'):
                self.config['advanced'] = True
                self.advanced_settings['thinking_interval'] = int(os.getenv('THINKING_INTERVAL_MINUTES', '3'))
                self.advanced_settings['followup_hours'] = int(os.getenv('FOLLOWUP_HOURS', '24'))
                self.advanced_settings['model_name'] = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')
                self.advanced_settings['enable_routines'] = os.getenv('ENABLE_ROUTINES', 'True').lower() == 'true'
                self.advanced_settings['enable_learning'] = os.getenv('ENABLE_LEARNING', 'True').lower() == 'true'
            
            # Check what's configured
            if not self.config['openai']:
                print(f"{Fore.RED}❌ OpenAI API key is missing!{Style.RESET_ALL}")
            if not self.config['telegram']:
                print(f"{Fore.RED}❌ Telegram bot token is missing!{Style.RESET_ALL}")
                
            if self.config['openai'] and self.config['telegram']:
                print(f"{Fore.GREEN}✅ Found complete configuration!{Style.RESET_ALL}")
                self.print_progress()
                return True  # Return True only if BOTH required keys exist
            else:
                print(f"{Fore.YELLOW}⚠️  Incomplete configuration found{Style.RESET_ALL}")
                self.print_progress()
                if not self.config['openai']:
                    print(f"\n{Fore.RED}Missing required: OpenAI API Key{Style.RESET_ALL}")
                if not self.config['telegram']:
                    print(f"{Fore.RED}Missing required: Telegram Bot Token{Style.RESET_ALL}")
                return False  # Return False if any required key is missing
        
        return False  # Return False if no .env file
    
    def final_summary(self):
        self.print_header()
        print(f"{Fore.GREEN}{Style.BRIGHT}🎉 SETUP COMPLETE!{Style.RESET_ALL}\n")
        
        self.print_progress()
        
        print(f"\n{Fore.CYAN}📋 Configuration Summary:{Style.RESET_ALL}")
        print(f"  Configuration saved to: {self.env_file}")
        if self.config['google']:
            print(f"  Google credentials: {self.credentials_file}")
        
        # Show advanced settings if configured
        if self.config['advanced']:
            print(f"\n{Fore.CYAN}⚙️  Advanced Settings:{Style.RESET_ALL}")
            print(f"  • AI Model: {self.advanced_settings['model_name']}")
            print(f"  • Thinking Interval: Every {self.advanced_settings['thinking_interval']} minutes")
            print(f"  • Follow-up Timing: After {self.advanced_settings['followup_hours']} hours")
            print(f"  • Routines: {'Enabled' if self.advanced_settings['enable_routines'] else 'Disabled'}")
            print(f"  • Learning: {'Enabled' if self.advanced_settings['enable_learning'] else 'Disabled'}")
        
        print(f"\n{Fore.GREEN}🚀 Next Steps:{Style.RESET_ALL}")
        print(f"1. Run the bot: {Fore.YELLOW}python autonomous_telegram_bot.py{Style.RESET_ALL}")
        print(f"2. Open Telegram and start chatting with your bot")
        print(f"3. Send /start to activate the autonomous features")
        
        if not self.config['google']:
            print(f"\n{Fore.YELLOW}⚠️  Note: Gmail/Calendar features are not configured{Style.RESET_ALL}")
        if not self.config['serper']:
            print(f"{Fore.YELLOW}⚠️  Note: Weather features are not configured{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}💡 Tips:{Style.RESET_ALL}")
        print(f"• The bot will think autonomously every {self.advanced_settings['thinking_interval']} minutes")
        print("• Set up routines with /add_routine command")
        print("• Check status anytime with /status command")
        print("• View insights with /insights command")
    
    def run(self):
        """Main wizard flow"""
        self.print_header()
        
        print(f"{Fore.WHITE}Welcome! This wizard will help you set up your Autonomous Virtual Secretary.{Style.RESET_ALL}")
        print(f"{Fore.WHITE}The setup will guide you through configuring all necessary API keys.{Style.RESET_ALL}")
        
        # Check for existing setup
        self.create_env_file()
        existing_config = self.check_existing_setup()
        
        # ALWAYS configure missing required keys, even if some optional ones exist
        needs_setup = not self.config['openai'] or not self.config['telegram']
        
        if needs_setup:
            print(f"\n{Fore.YELLOW}Some required configurations are missing.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Let's set them up now!{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            
            # Required setups
            self.print_header()
            print(f"{Fore.RED}{Style.BRIGHT}REQUIRED CONFIGURATIONS{Style.RESET_ALL}")
            print(f"{Fore.WHITE}These are essential for the bot to function.{Style.RESET_ALL}")
            
            # ALWAYS ask for OpenAI if missing
            if not self.config['openai']:
                print(f"\n{Fore.RED}➤ OpenAI API Key is REQUIRED and MISSING{Style.RESET_ALL}")
                self.setup_openai()
                self.print_progress()
            
            # ALWAYS ask for Telegram if missing  
            if not self.config['telegram']:
                print(f"\n{Fore.RED}➤ Telegram Bot Token is REQUIRED and MISSING{Style.RESET_ALL}")
                self.setup_telegram()
                self.print_progress()
        elif existing_config:
            # Both required keys exist, offer to use or reconfigure
            print(f"\n{Fore.GREEN}All required configurations found!{Style.RESET_ALL}")
            use_existing = self.get_input("\nUse existing configuration? (y/n)").lower()
            if use_existing == 'y':
                self.final_summary()
                return
            print(f"\n{Fore.YELLOW}Let's reconfigure!{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            
            # Allow reconfiguration
            self.setup_openai()
            self.setup_telegram()
            self.print_progress()
        
        # Optional setups
        self.print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}OPTIONAL CONFIGURATIONS{Style.RESET_ALL}")
        print(f"{Fore.WHITE}These enhance functionality but aren't required.{Style.RESET_ALL}")
        
        # Google Setup
        if not self.config['google']:
            self.setup_google()
            self.print_progress()
        
        # Serper Setup
        if not self.config['serper']:
            self.setup_serper()
            self.print_progress()
        
        # Advanced Settings
        if not self.config['advanced']:
            self.setup_advanced()
            self.print_progress()
        
        # Final summary
        self.final_summary()
        
        # Ask if user wants to start the bot now
        print()
        start_now = self.get_input("\n🚀 Start the bot now? (y/n)").lower()
        if start_now == 'y':
            print(f"\n{Fore.GREEN}Starting Autonomous Virtual Secretary...{Style.RESET_ALL}\n")
            time.sleep(2)
            try:
                subprocess.run([sys.executable, 'autonomous_telegram_bot.py'])
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Bot stopped. You can start it anytime with:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}python autonomous_telegram_bot.py{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        wizard = SetupWizard()
        wizard.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Setup cancelled by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Setup error: {e}{Style.RESET_ALL}")
        sys.exit(1)