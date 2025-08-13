#!/usr/bin/env python3

import os
import asyncio
import signal
import sys
import subprocess
from datetime import datetime
from typing import Dict, Set, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from autonomous_secretary import AutonomousSecretary
from memory_store import TaskType

load_dotenv()

class AutonomousTelegramBot:
    def __init__(self):
        self.token: str = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Get thinking interval from env or default to 3 minutes
        self.thinking_interval_minutes = int(os.getenv('THINKING_INTERVAL_MINUTES', '3'))
        
        self.secretary: AutonomousSecretary = AutonomousSecretary()
        self.application: Application = Application.builder().token(self.token).build()
        self.bot: Bot = Bot(self.token)
        self.thinking_task: Optional[asyncio.Task] = None
        self.admin_chat_ids: Set[int] = set()  # Store admin chat IDs
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(CommandHandler("routines", self.manage_routines))
        self.application.add_handler(CommandHandler("add_routine", self.add_routine))
        self.application.add_handler(CommandHandler("insights", self.show_insights))
        self.application.add_handler(CommandHandler("pending", self.show_pending))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        self.admin_chat_ids.add(update.effective_chat.id)
        
        welcome_message = """
🤖 **Autonomous Virtual Secretary Activated**

I'm your intelligent secretary that works continuously in the background. I can:

**Core Capabilities:**
📧 Send and monitor emails
📅 Manage your calendar
🔄 Send follow-up reminders automatically
🧠 Learn from patterns and act proactively
⏰ Execute routine tasks
🌤️ Provide information when needed

**Autonomous Features:**
• I continuously think about what needs to be done
• I send follow-ups when responses are overdue
• I prepare for upcoming meetings
• I learn your patterns and preferences
• I take initiative based on context

**Commands:**
/help - Show available commands
/status - View my current thinking status
/routines - Manage automated routines
/insights - See what I've learned
/pending - View pending tasks

Just talk to me naturally, and I'll handle the rest!

*I'm now running in autonomous mode and will check for tasks every {self.thinking_interval_minutes} minutes.*
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
        # Start the autonomous thinking process if not already running
        if self.thinking_task is None:
            self.thinking_task = asyncio.create_task(self._run_autonomous_thinking(update.effective_chat.id))
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_message = """
📚 **Available Commands**

**Basic Commands:**
/start - Activate the secretary
/help - Show this help message
/status - Check autonomous thinking status

**Task Management:**
/pending - View all pending tasks
/routines - List active routines
/add_routine - Add a new routine task

**Intelligence:**
/insights - View learned patterns and insights

**Example Requests:**
• "Email John about the quarterly report and follow up if he doesn't respond in 2 days"
• "Schedule a meeting tomorrow at 3 PM and remind me to prepare 1 hour before"
• "Check the weather every morning at 7 AM"
• "Send weekly status reports every Friday"

I understand context and will act accordingly. For example, if you ask me to send an email and the recipient doesn't respond, I'll automatically follow up.
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pending_tasks = self.secretary.memory.get_pending_tasks()
        followup_tasks = self.secretary.memory.get_tasks_requiring_followup(self.secretary.followup_hours)
        routines = self.secretary.memory.get_due_routines() if self.secretary.enable_routines else []
        
        status_message = f"""
📊 **Autonomous Secretary Status**

🕐 **Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
🧠 **Thinking Status:** {'Active' if self.thinking_task and not self.thinking_task.done() else 'Inactive'}
⏱️ **Last Check:** {self.secretary.last_proactive_check.strftime('%H:%M')}
🔄 **Check Interval:** Every {self.thinking_interval_minutes} minutes

**Active Tasks:**
• Pending: {len(pending_tasks)}
• Awaiting Response: {len(followup_tasks)}
• Due Routines: {len(routines)}

**Memory Stats:**
• Total Tasks: {len(self.secretary.memory.memory['tasks'])}
• Learned Patterns: {len(self.secretary.memory.memory['patterns'])}
• Insights: {len(self.secretary.memory.memory['insights'])}

I'm continuously monitoring and will act when needed.
        """
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def show_pending(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pending_tasks = self.secretary.memory.get_pending_tasks()
        
        if not pending_tasks:
            await update.message.reply_text("✅ No pending tasks at the moment!")
            return
        
        message = "📋 **Pending Tasks:**\n\n"
        for task in pending_tasks[:10]:  # Show max 10 tasks
            task_type = task.get('type', 'Unknown')
            created = task.get('created_at', 'Unknown')
            status = task.get('status', 'Unknown')
            
            message += f"• **Type:** {task_type}\n"
            message += f"  **Status:** {status}\n"
            message += f"  **Created:** {created[:16]}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def show_insights(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        insights = self.secretary.memory.memory.get('insights', [])[-5:]
        
        if not insights:
            await update.message.reply_text("No insights gathered yet. I'll learn as we interact!")
            return
        
        message = "🧠 **Recent Insights:**\n\n"
        for insight in insights:
            message += f"• {insight['insight']}\n"
            message += f"  _{insight['timestamp'][:16]}_\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def manage_routines(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        routines = self.secretary.memory.memory.get('routines', {})
        
        if not routines:
            message = "No routines set up yet.\n\nUse /add_routine to create one!"
        else:
            message = "⏰ **Active Routines:**\n\n"
            for routine_id, routine in routines.items():
                message += f"• **{routine.get('name', 'Unnamed')}**\n"
                message += f"  Frequency: {routine.get('frequency', 'Unknown')}\n"
                message += f"  Last Run: {routine.get('last_executed', 'Never')[:16] if routine.get('last_executed') else 'Never'}\n"
                message += f"  Executions: {routine.get('execution_count', 0)}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def add_routine(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        instruction = """
To add a routine, send a message in this format:

"Create routine: [name] | [frequency] | [action]"

**Frequency options:** hourly, daily, weekly

**Examples:**
• "Create routine: Morning Brief | daily | Check weather and list today's calendar events"
• "Create routine: Team Update | weekly | Send status report to team@company.com"
• "Create routine: Inbox Check | hourly | Check for urgent emails"
        """
        
        await update.message.reply_text(instruction, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        message = update.message.text
        
        # Log the incoming message
        print(f"📨 Received message from {user_id}: {message[:100]}...")
        
        # Check if it's a routine creation request
        if message.lower().startswith("create routine:"):
            await self._create_routine_from_message(update, message)
            return
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Process the message with a timeout
            response = await asyncio.wait_for(
                self.secretary.process_user_message(user_id, message),
                timeout=30.0  # 30 second timeout
            )
            
            # Send response (split if too long for Telegram)
            if len(response) > 4000:
                # Split long responses
                parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for part in parts:
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(response)
            
            # If this looks like it needs follow-up, note it
            if any(phrase in message.lower() for phrase in ["follow up", "remind", "check back", "if no response"]):
                await update.message.reply_text(
                    "📝 *Note:* I'll monitor this task and follow up automatically if needed.",
                    parse_mode='Markdown'
                )
                
        except asyncio.TimeoutError:
            print(f"⏱️ Timeout processing message from {user_id}")
            await update.message.reply_text(
                "I'm taking a bit longer to process your request. Please wait a moment and I'll get back to you soon!"
            )
        except Exception as e:
            print(f"❌ Error handling message: {e}")
            await update.message.reply_text(
                "I apologize, but I encountered an issue processing your message. Please try again or type /help for assistance."
            )
    
    async def _create_routine_from_message(self, update: Update, message: str):
        try:
            # Parse the routine format: "Create routine: name | frequency | action"
            parts = message.replace("Create routine:", "").strip().split("|")
            
            if len(parts) != 3:
                await update.message.reply_text("❌ Invalid format. Please use: name | frequency | action")
                return
            
            name = parts[0].strip()
            frequency = parts[1].strip().lower()
            action = parts[2].strip()
            
            if frequency not in ["hourly", "daily", "weekly"]:
                await update.message.reply_text("❌ Frequency must be: hourly, daily, or weekly")
                return
            
            routine_id = self.secretary.create_routine({
                "name": name,
                "frequency": frequency,
                "action": action,
                "enabled": True,
                "chat_id": update.effective_chat.id
            })
            
            await update.message.reply_text(
                f"✅ Routine '{name}' created!\n\nIt will run {frequency} and: {action}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error creating routine: {str(e)}")
    
    async def _run_autonomous_thinking(self, chat_id: int):
        """
        Background task that runs the autonomous thinking process
        """
        await asyncio.sleep(10)  # Initial delay
        
        while True:
            try:
                print(f"🤔 Autonomous thinking cycle started at {datetime.now()}")
                
                # Run the thinking process
                decision = await self.secretary.think_and_act()
                
                # Notify admin if important action was taken
                if decision.get("action_needed") and decision.get("priority") == "high":
                    notification = f"""
🚨 **Autonomous Action Taken**

**Action:** {decision.get('primary_action')}
**Priority:** {decision.get('priority')}
**Reasoning:** {decision.get('reasoning', 'No reasoning provided')[:200]}...
                    """
                    
                    # Send notification to all admin chats
                    for admin_chat_id in self.admin_chat_ids:
                        try:
                            await self.bot.send_message(
                                chat_id=admin_chat_id,
                                text=notification,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            print(f"Failed to send notification to {admin_chat_id}: {e}")
                
                # Check and execute due routines
                due_routines = self.secretary.memory.get_due_routines()
                for routine in due_routines:
                    await self._execute_routine(routine)
                
                # Wait before next thinking cycle
                await asyncio.sleep(self.thinking_interval_minutes * 60)
                
            except Exception as e:
                print(f"Error in autonomous thinking: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def _execute_routine(self, routine: Dict):
        """
        Execute a routine task
        """
        try:
            routine_id = routine.get('routine_id')
            action = routine.get('action', '')
            chat_id = routine.get('chat_id')
            
            # Process the routine action
            result = await self.secretary.process_user_message(
                user_id=f"routine_{routine_id}",
                message=action
            )
            
            # Update routine execution
            self.secretary.memory.update_routine_execution(routine_id)
            
            # Send result to the appropriate chat if configured
            if chat_id:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"⏰ **Routine: {routine.get('name', 'Unnamed')}**\n\n{result}",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            print(f"Error executing routine {routine.get('name')}: {e}")
    
    def run(self):
        """
        Start the bot
        """
        print("🤖 Autonomous Telegram Secretary starting...")
        print(f"✅ Bot token configured")
        print(f"🧠 Autonomous thinking enabled (every {self.thinking_interval_minutes} minutes)")
        print("📡 Waiting for connections...")
        
        # Set up graceful shutdown
        def signal_handler(sig, frame):
            print("\n👋 Shutting down gracefully...")
            if self.thinking_task:
                self.thinking_task.cancel()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        # Load environment first
        load_dotenv()
        
        # Check if running directly (not from start.py)
        if not os.getenv('OPENAI_API_KEY') or not os.getenv('TELEGRAM_BOT_TOKEN'):
            print("❌ Missing required configuration!")
            print("\n🔧 Running setup wizard...")
            print("Alternatively, you can run: python start.py\n")
            
            import subprocess
            try:
                subprocess.run([sys.executable, 'setup_wizard.py'], check=True)
                # Reload environment after setup
                load_dotenv()
            except subprocess.CalledProcessError:
                print("❌ Setup failed or was cancelled")
                sys.exit(1)
        
        # Final check
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY not configured")
            print("Please run: python setup_wizard.py")
            sys.exit(1)
        
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            print("❌ TELEGRAM_BOT_TOKEN not configured")
            print("Please run: python setup_wizard.py")
            sys.exit(1)
        
        # Start the bot
        bot = AutonomousTelegramBot()
        bot.run()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print("\nFor help, run: python setup_wizard.py")
        sys.exit(1)