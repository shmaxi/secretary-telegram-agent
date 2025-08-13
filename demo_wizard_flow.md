# Setup Wizard Flow

## When .env file doesn't exist (your current situation):

1. **Wizard creates .env file**
2. **Asks for OpenAI API Key** ← You'll be prompted here!
3. **Asks for Telegram Bot Token**
4. **Optional: Google Services**
5. **Optional: Serper API**
6. **Optional: Advanced Settings**

## The wizard WILL ask for your OpenAI key because:

- No .env file exists
- No OPENAI_API_KEY is set
- The wizard detects this as missing required configuration

## To run the wizard and be asked for your OpenAI key:

```bash
python setup_wizard.py
```

Or use the start script which will run the wizard if setup is incomplete:

```bash
python start.py
```

## What you'll see:

```
🔑 OPENAI API SETUP
──────────────────────────────────────────────────
OpenAI API is REQUIRED for the AI intelligence.

Steps to get your API key:
1. Go to https://platform.openai.com/signup
2. Sign up or log in
3. Go to API Keys section
4. Create new secret key
5. Copy the key (it won't be shown again!)

Note: Keys start with 'sk-' and are about 50 characters long

Open OpenAI website now? (y/n): 
➤ Enter your OpenAI API key: [YOUR KEY HERE]
```

The wizard will:
1. Validate your key
2. Save it to .env
3. Confirm it was saved
4. Continue with other configurations