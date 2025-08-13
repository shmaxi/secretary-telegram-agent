# Autonomous Virtual Secretary - Telegram Bot

An intelligent, self-thinking virtual secretary that runs exclusively through Telegram. Built with CrewAI, this secretary continuously monitors tasks, makes decisions, and takes proactive actions without requiring constant user input.

## 🧠 Key Features

### Autonomous Intelligence
- **Continuous Thinking**: Runs background analysis every 3 minutes (configurable)
  - More responsive than typical 15-30 minute intervals
  - Catches urgent tasks quickly
  - Better mimics human assistant behavior
- **Proactive Actions**: Automatically sends follow-ups, reminders, and updates
- **Pattern Learning**: Learns from interactions and adapts behavior
- **Smart Decision Making**: Evaluates context and priorities to decide next actions

### Core Capabilities
- **📧 Email Management**: Send emails and automatically follow up on unanswered messages
- **📅 Calendar Integration**: Schedule meetings and prepare reminders before events
- **🔄 Task Monitoring**: Track pending tasks and escalate when needed
- **⏰ Routine Automation**: Execute recurring tasks on schedule
- **🌤️ Information Gathering**: Check weather and other information proactively
- **💬 24/7 Telegram Access**: Always available through Telegram chat

## 🚀 Quick Start

### Prerequisites
- Python 3.10 - 3.13
- Telegram account

### Installation

1. **Clone or download the project**
```bash
cd virtual-secretary
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the setup wizard**
```bash
python start.py
```

The interactive wizard will guide you through:
- Creating API accounts
- Configuring all services
- Validating your keys
- Starting the bot

4. **Start chatting with your bot on Telegram!**

### Alternative: Manual Setup

If you prefer manual configuration:
```bash
cp .env.example .env
# Edit .env with your API keys
python autonomous_telegram_bot.py
```

Or add just the OpenAI key:
```bash
python add_openai_key.py
```

## 🔧 Setup Wizard

The setup wizard (`python start.py`) provides:
- **Step-by-step guidance** for each API configuration
- **Automatic validation** of all API keys
- **Direct links** to registration pages
- **Copy-paste friendly** instructions
- **Progress tracking** throughout setup
- **Advanced settings configuration**:
  - AI model selection (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
  - Thinking interval (1-60 minutes)
  - Follow-up timing (1-168 hours)
  - Feature toggles (routines, learning)
- **Automatic bot launch** after setup

## 🔑 API Setup Details

### Required APIs

1. **OpenAI API** (Required for AI intelligence)
   - Sign up at [OpenAI](https://platform.openai.com)
   - Generate API key in dashboard
   - The wizard will validate your key automatically

2. **Telegram Bot Token** (Required for messaging)
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create new bot with `/newbot`
   - The wizard will guide you through this process

### Optional APIs

3. **Google APIs** (For Gmail & Calendar features)
   - Enable APIs in [Google Cloud Console](https://console.cloud.google.com)
   - Download OAuth credentials
   - The wizard provides detailed steps

4. **Serper API** (For weather information)
   - Get free key at [Serper](https://serper.dev)
   - 2,500 free queries per month
   - The wizard can open the signup page for you

## 💬 Telegram Commands

- `/start` - Activate the autonomous secretary
- `/status` - View current thinking status and statistics
- `/pending` - List all pending tasks
- `/routines` - Manage automated routines
- `/add_routine` - Create new routine task
- `/insights` - View learned patterns
- `/help` - Show available commands

## 🤖 Autonomous Behaviors

### Automatic Follow-ups
```
You: "Send an email to john@example.com about the project deadline"
Bot: "Email sent!"
*24 hours later without response*
Bot: "John hasn't responded to your email about the project deadline. I'm sending a follow-up reminder."
```

### Proactive Reminders
```
You: "Schedule a meeting with the team tomorrow at 2 PM"
Bot: "Meeting scheduled!"
*Next day at 1 PM*
Bot: "Reminder: You have a team meeting in 1 hour. Would you like me to prepare anything?"
```

### Pattern Recognition
```
*After noticing you check weather every morning*
Bot: "I've noticed you check the weather each morning. Would you like me to send you a weather update daily at 7 AM?"
```

## ⏰ Creating Routines

Send a message in this format:
```
Create routine: [name] | [frequency] | [action]
```

### Examples:
- `Create routine: Morning Brief | daily | Check weather and list today's events`
- `Create routine: Weekly Report | weekly | Send status update to manager@company.com`
- `Create routine: Inbox Monitor | hourly | Check for urgent emails`

## 🧠 How It Works

1. **Continuous Thinking Loop**: Every 3 minutes (default), the secretary:
   - Analyzes pending tasks
   - Checks for overdue follow-ups
   - Evaluates routine schedules
   - Makes decisions on next actions

2. **Memory System**: Maintains persistent storage of:
   - Task states and history
   - User preferences and patterns
   - Conversation context
   - Learned insights

3. **Decision Engine**: Uses CrewAI agents to:
   - Analyze situations
   - Prioritize actions
   - Execute decisions
   - Monitor results

## 📁 Project Structure

```
virtual-secretary/
├── autonomous_telegram_bot.py  # Main bot with autonomous features
├── autonomous_secretary.py     # Core intelligence and decision engine
├── memory_store.py            # Persistent memory and learning
├── tools/                     # Integration tools
│   ├── gmail_tool.py         
│   ├── calendar_tool.py      
│   └── weather_tool.py       
├── requirements.txt           
├── .env.example              
└── secretary_memory.json      # Persistent memory storage (auto-created)
```

## 🔒 Security & Privacy

- All data stored locally in `secretary_memory.json`
- API keys never shared or logged
- Conversations remain private
- Memory can be cleared by deleting the JSON file

## 🛠️ Customization

### Quick Reconfiguration
Change settings without re-entering API keys:
```bash
python reconfigure.py
```

### Manual Configuration
Edit `.env` file directly:
```bash
# AI Model
OPENAI_MODEL_NAME=gpt-4o

# Thinking frequency (minutes)
THINKING_INTERVAL_MINUTES=5

# Follow-up timing (hours)
FOLLOWUP_HOURS=12

# Feature toggles
ENABLE_ROUTINES=True
ENABLE_LEARNING=True
```

### Available Settings
- **AI Models**: gpt-4o-mini (default), gpt-4o, gpt-3.5-turbo
- **Thinking Interval**: 1-60 minutes (default: 3)
- **Follow-up Timing**: 1-168 hours (default: 24)
- **Routines**: Enable/disable automated routines
- **Learning**: Enable/disable pattern learning

## 📝 Example Interactions

### Complex Request with Auto-Follow-up
```
You: "Email the team about tomorrow's deadline and make sure everyone confirms"
Bot: "I've sent the email to the team. I'll monitor for responses and follow up with anyone who doesn't confirm within 24 hours."
```

### Learning User Preferences
```
Bot: "I've noticed you usually schedule meetings in the afternoon. Shall I default to 2 PM for future meeting requests when no time is specified?"
```

## 🐛 Troubleshooting

### Common Issues

**Installation Errors:**
```bash
# Test your setup
python test_setup.py

# If packages missing
pip install -r requirements.txt
```

**Bot Not Starting:**
- Run `python test_setup.py` to check configuration
- Ensure both OPENAI_API_KEY and TELEGRAM_BOT_TOKEN are set
- Try running the setup wizard: `python setup_wizard.py`

**Pydantic Warnings:**
- The deprecation warnings about `Field` and `asyncio.get_event_loop()` are normal
- They don't affect functionality and can be ignored

**Bot Not Responding:**
- Check TELEGRAM_BOT_TOKEN is correct
- Make sure you've started chat with `/start` command
- Verify bot is running (check console output)

**No Autonomous Actions:**
- Verify OPENAI_API_KEY is valid
- Check console for thinking cycle messages
- Default interval is 3 minutes (watch console output)

**Google Services Not Working:**
- Ensure credentials.json exists
- First use requires browser authorization
- Delete token.pickle files to re-authenticate

**Memory Issues:**
- Delete `secretary_memory.json` to reset all memory
- The bot will create a new one automatically

## 📄 License

MIT License - Use freely for personal or commercial projects.