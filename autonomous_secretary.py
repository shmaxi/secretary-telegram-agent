import os
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from crewai import Agent, Crew, Task, Process
from dotenv import load_dotenv
from memory_store import MemoryStore, TaskStatus, TaskType
from tools.gmail_tool import GmailTool
from tools.gmail_read_tool import GmailReadTool, CheckEmailResponsesTool
from tools.calendar_tool import GoogleCalendarTool, ListCalendarEventsTool
from tools.weather_tool import WeatherTool

load_dotenv()

class AutonomousSecretary:
    def __init__(self, telegram_chat_id: Optional[str] = None):
        self.memory = MemoryStore()
        self.telegram_chat_id = telegram_chat_id
        self.gmail_tool = GmailTool()
        self.gmail_read_tool = GmailReadTool()
        self.check_responses_tool = CheckEmailResponsesTool()
        self.calendar_tool = GoogleCalendarTool()
        self.list_events_tool = ListCalendarEventsTool()
        self.weather_tool = WeatherTool()
        self.last_proactive_check = datetime.now()
        
        # Load configuration
        self.followup_hours = int(os.getenv('FOLLOWUP_HOURS', '24'))
        self.enable_routines = os.getenv('ENABLE_ROUTINES', 'True').lower() == 'true'
        self.enable_learning = os.getenv('ENABLE_LEARNING', 'True').lower() == 'true'
        
    def thinking_agent(self) -> Agent:
        return Agent(
            role='Strategic Thinking Secretary',
            goal='Continuously analyze situations, identify needed actions, and make proactive decisions',
            backstory="""You are an intelligent secretary with the ability to think ahead and anticipate needs.
            You analyze patterns, remember past interactions, and proactively take actions to help.
            You can identify when follow-ups are needed, when reminders should be sent, and when to check on pending tasks.
            You think like a human assistant would - considering context, timing, and relationships.""",
            verbose=True,
            allow_delegation=True,
            max_iter=5
        )
    
    def execution_agent(self) -> Agent:
        return Agent(
            role='Task Execution Specialist',
            goal='Execute tasks efficiently based on strategic decisions',
            backstory="""You execute tasks with precision. You handle emails, calendar events, 
            and other actions. You report back on success or failure of tasks.""",
            tools=[
                self.gmail_tool,
                self.gmail_read_tool,
                self.check_responses_tool,
                self.calendar_tool,
                self.list_events_tool,
                self.weather_tool
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def monitoring_agent(self) -> Agent:
        return Agent(
            role='Task Monitor',
            goal='Monitor ongoing tasks and identify what needs attention',
            backstory="""You continuously monitor all ongoing tasks, check for responses, 
            track deadlines, and identify when intervention is needed. You're like a radar 
            system that never misses anything important.""",
            tools=[
                self.gmail_read_tool,
                self.check_responses_tool,
                self.list_events_tool
            ],
            verbose=True,
            allow_delegation=False
        )
    
    async def think_and_act(self) -> Dict:
        """
        Main autonomous thinking process that decides what to do next
        """
        # Get current context
        pending_tasks = self.memory.get_pending_tasks()
        followup_tasks = self.memory.get_tasks_requiring_followup(self.followup_hours)
        due_routines = self.memory.get_due_routines() if self.enable_routines else []
        
        # Build context for decision making
        context = {
            "current_time": datetime.now().isoformat(),
            "pending_tasks": pending_tasks,
            "tasks_needing_followup": followup_tasks,
            "due_routines": due_routines,
            "recent_insights": self.memory.memory.get("insights", [])[-5:]
        }
        
        # Create thinking task
        thinking_task = Task(
            description=f"""
            Analyze the current situation and decide what actions to take:
            
            Current Context:
            {context}
            
            Consider:
            1. Check emails for any responses to pending requests (use Check Email Responses tool)
            2. Are there any tasks that haven't received responses and need follow-up?
            3. Are there upcoming calendar events that need preparation?
            4. Check for new unread emails that might need attention (use Read Gmail tool)
            5. Are there patterns suggesting routine tasks that should be done?
            6. Is there anything proactive that would be helpful?
            7. Should any pending tasks be escalated or modified?
            
            Provide a structured decision about what to do next, including:
            - Primary action to take (if any)
            - Reasoning for the action
            - Priority level (high/medium/low)
            - Any follow-up actions needed
            """,
            expected_output="Structured decision about next actions with reasoning",
            agent=self.thinking_agent()
        )
        
        monitoring_task = Task(
            description=f"""
            Monitor and check status of all ongoing tasks:
            
            Pending Tasks: {pending_tasks}
            
            Actions to take:
            1. Check for email responses from people we're waiting to hear from
            2. Review unread emails for urgent matters
            3. Check upcoming calendar events
            4. Identify any tasks that are overdue or need follow-up
            
            Check for:
            - Tasks stuck in waiting state too long
            - Failed tasks that should be retried
            - Patterns of similar requests
            - Opportunities for optimization
            """,
            expected_output="List of tasks requiring attention with recommendations",
            agent=self.monitoring_agent()
        )
        
        try:
            crew = Crew(
                agents=[self.thinking_agent(), self.monitoring_agent()],
                tasks=[thinking_task, monitoring_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Parse and execute decisions
            decision = self._parse_decision(str(result))
            
            if decision.get("action_needed"):
                await self._execute_decision(decision)
            
            return decision
            
        except Exception as e:
            return {"error": str(e), "action_needed": False}
    
    def _parse_decision(self, result: str) -> Dict:
        """
        Parse the AI's decision into actionable items
        """
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        decision = {
            "action_needed": False,
            "primary_action": None,
            "priority": "medium",
            "reasoning": result,
            "follow_up_actions": []
        }
        
        result_lower = result.lower()
        
        # Detect if action is needed
        if any(keyword in result_lower for keyword in ["send", "schedule", "remind", "follow up", "check", "create"]):
            decision["action_needed"] = True
            
            # Determine action type
            if "follow up" in result_lower or "follow-up" in result_lower or "reminder" in result_lower:
                decision["primary_action"] = "send_followup"
            elif "schedule" in result_lower or "calendar" in result_lower:
                decision["primary_action"] = "schedule_event"
            elif "email" in result_lower or "send" in result_lower:
                decision["primary_action"] = "send_email"
            elif "check" in result_lower and "weather" in result_lower:
                decision["primary_action"] = "check_weather"
            
            # Determine priority
            if "urgent" in result_lower or "immediately" in result_lower or "asap" in result_lower:
                decision["priority"] = "high"
            elif "low priority" in result_lower or "when possible" in result_lower:
                decision["priority"] = "low"
        
        return decision
    
    async def _execute_decision(self, decision: Dict) -> Dict:
        """
        Execute the decision made by the thinking agent
        """
        action = decision.get("primary_action")
        
        if not action:
            return {"status": "no_action"}
        
        execution_task = Task(
            description=f"""
            Execute the following action: {action}
            
            Context: {decision.get('reasoning', '')}
            Priority: {decision.get('priority', 'medium')}
            
            Use the appropriate tools to complete this action and report the result.
            """,
            expected_output="Confirmation of action completion with details",
            agent=self.execution_agent()
        )
        
        try:
            crew = Crew(
                agents=[self.execution_agent()],
                tasks=[execution_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Log the execution
            task_id = str(uuid.uuid4())
            self.memory.add_task(task_id, {
                "type": action,
                "decision": decision,
                "result": str(result),
                "status": TaskStatus.COMPLETED.value
            })
            
            return {"status": "completed", "result": str(result)}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def process_user_message(self, user_id: str, message: str) -> str:
        """
        Process a message from a user and respond
        """
        try:
            # Get user context
            user_context = self.memory.get_user_context(user_id)
            
            # Let the AI decide what to do with EVERY message
            process_task = Task(
                description=f"""
                Process this message from the user: {message}
                
                User context:
                - Recent conversations: {user_context.get('conversations', [])}
                - Known preferences: {user_context.get('preferences', {})}
                - Pending tasks: {self.memory.get_pending_tasks()}
                
                Analyze the message and decide:
                1. Is this a greeting, question, request, or conversation?
                2. Does it require using tools (email, calendar, weather, etc.)?
                3. What is the appropriate response?
                
                If action is needed, use the available tools to complete it.
                If it's a question, provide a helpful answer.
                If it's a greeting or conversation, respond naturally.
                
                Remember: You are a virtual secretary. Be helpful, professional, and proactive.
                """,
                expected_output="Appropriate response to the user based on the context and request",
                agent=self.execution_agent()
            )
            
            crew = Crew(
                agents=[self.execution_agent()],
                tasks=[process_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            response = str(result)
            
            # Store conversation
            self.memory.add_conversation(user_id, message, response)
            
            # Let the AI's response determine if this created a task
            # The AI will mention if it scheduled something, sent an email, etc.
            # We can parse the response to understand what was done
            
            # Learn from interaction
            self._learn_from_interaction(user_id, message, response)
            
            return response
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error processing your message: {str(e)}\n\nPlease try rephrasing your request or type /help for available commands."
            print(f"Error in process_user_message: {e}")
            return error_msg
    
    
    def _learn_from_interaction(self, user_id: str, message: str, response: str):
        """
        Learn patterns from user interactions
        """
        if not self.enable_learning:
            return
            
        # Extract time patterns
        now = datetime.now()
        hour = now.hour
        
        if "meeting" in message.lower() or "schedule" in message.lower():
            self.memory.learn_pattern(user_id, "scheduling_preferences", {
                "time_of_request": hour,
                "day_of_week": now.strftime("%A"),
                "request_type": "scheduling"
            })
        
        if "email" in message.lower():
            self.memory.learn_pattern(user_id, "communication_preferences", {
                "time_of_request": hour,
                "request_type": "email"
            })
        
        # Add insight if pattern detected
        if hour >= 9 and hour <= 10:
            self.memory.add_insight(
                f"User {user_id} often makes requests in the morning",
                "user_behavior"
            )
    
    async def run_continuous_thinking(self, interval_minutes: int = 3):
        """
        Run the thinking process continuously at specified intervals
        """
        while True:
            try:
                # Check if enough time has passed
                if (datetime.now() - self.last_proactive_check) > timedelta(minutes=interval_minutes):
                    print(f"🤔 Running autonomous thinking cycle at {datetime.now()}")
                    
                    decision = await self.think_and_act()
                    
                    if decision.get("action_needed"):
                        print(f"📌 Taking action: {decision.get('primary_action')}")
                    else:
                        print("✅ No immediate action needed")
                    
                    self.last_proactive_check = datetime.now()
                
                # Short sleep to prevent CPU overuse
                await asyncio.sleep(30)  # Check every 30 seconds if it's time to think
                
            except Exception as e:
                print(f"Error in thinking cycle: {e}")
                await asyncio.sleep(60)
    
    def create_routine(self, routine_data: Dict):
        """
        Create a new routine task
        """
        routine_id = str(uuid.uuid4())
        self.memory.add_routine(routine_id, routine_data)
        return routine_id