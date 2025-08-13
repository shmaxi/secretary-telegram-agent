# 🚀 Virtual Secretary - Quick Start Guide

## 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the setup wizard
python start.py

# 3. Follow the prompts - Done!
```

## What You Get

An **autonomous AI secretary** that:
- 🧠 **Thinks every 3 minutes** - Makes decisions proactively
- 📧 **Manages emails** - Sends and auto-follows up
- 📅 **Handles calendar** - Schedules and reminds
- 🔄 **Learns patterns** - Adapts to your behavior
- 💬 **Always available** - 24/7 via Telegram

## Key Commands in Telegram

- `/start` - Activate the secretary
- `/status` - Check what it's thinking
- `/routines` - Set up automated tasks
- `/pending` - View active tasks

## Example: Auto Follow-up

```
You: "Email john@example.com about the report"
Bot: "Email sent!"

*24 hours later if no response*
Bot: "John hasn't responded. Sending a follow-up."
```

## Test Your Setup

```bash
python test_setup.py
```

This shows exactly what's configured and what's missing.

## Need Help?

1. Run `python setup_wizard.py` for guided setup
2. Check `README.md` for detailed documentation
3. The wizard validates everything automatically

## Files Created

- `.env` - Your API keys (keep private!)
- `secretary_memory.json` - Bot's memory (auto-created)
- `*.pickle` - Google auth tokens (if using Gmail/Calendar)

## Start the Bot

Three ways to start:
```bash
python start.py              # Recommended - checks setup first
python autonomous_telegram_bot.py  # Direct start
python setup_wizard.py       # Re-run setup anytime
```

That's it! Your autonomous secretary is ready to work for you 24/7.