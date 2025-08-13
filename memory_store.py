import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_RESPONSE = "waiting_response"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    REMINDER = "reminder"
    FOLLOW_UP = "follow_up"
    WEATHER_CHECK = "weather_check"
    ROUTINE_CHECK = "routine_check"
    CUSTOM = "custom"

class MemoryStore:
    def __init__(self, storage_path: str = "secretary_memory.json"):
        self.storage_path = storage_path
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                return self._initialize_memory()
        return self._initialize_memory()
    
    def _initialize_memory(self) -> Dict:
        return {
            "tasks": {},
            "conversations": {},
            "patterns": {},
            "relationships": {},
            "preferences": {},
            "routines": {},
            "pending_actions": [],
            "completed_actions": [],
            "insights": []
        }
    
    def save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2, default=str)
    
    def add_task(self, task_id: str, task_data: Dict) -> None:
        self.memory["tasks"][task_id] = {
            **task_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": TaskStatus.PENDING.value
        }
        self.save()
    
    def update_task(self, task_id: str, updates: Dict) -> None:
        if task_id in self.memory["tasks"]:
            self.memory["tasks"][task_id].update(updates)
            self.memory["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
            self.save()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.memory["tasks"].get(task_id)
    
    def get_pending_tasks(self) -> List[Dict]:
        pending = []
        for task_id, task in self.memory["tasks"].items():
            if task.get("status") in [TaskStatus.PENDING.value, TaskStatus.WAITING_RESPONSE.value]:
                task["task_id"] = task_id
                pending.append(task)
        return pending
    
    def add_conversation(self, user_id: str, message: str, response: str):
        if user_id not in self.memory["conversations"]:
            self.memory["conversations"][user_id] = []
        
        self.memory["conversations"][user_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "assistant_response": response
        })
        
        # Keep only last 100 messages per user
        if len(self.memory["conversations"][user_id]) > 100:
            self.memory["conversations"][user_id] = self.memory["conversations"][user_id][-100:]
        
        self.save()
    
    def get_user_context(self, user_id: str) -> Dict:
        return {
            "conversations": self.memory["conversations"].get(user_id, [])[-10:],
            "preferences": self.memory["preferences"].get(user_id, {}),
            "patterns": self.memory["patterns"].get(user_id, {})
        }
    
    def learn_pattern(self, user_id: str, pattern_type: str, pattern_data: Dict):
        if user_id not in self.memory["patterns"]:
            self.memory["patterns"][user_id] = {}
        
        if pattern_type not in self.memory["patterns"][user_id]:
            self.memory["patterns"][user_id][pattern_type] = []
        
        self.memory["patterns"][user_id][pattern_type].append({
            "data": pattern_data,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.5
        })
        
        self.save()
    
    def add_routine(self, routine_id: str, routine_data: Dict):
        self.memory["routines"][routine_id] = {
            **routine_data,
            "created_at": datetime.now().isoformat(),
            "last_executed": None,
            "execution_count": 0
        }
        self.save()
    
    def update_routine_execution(self, routine_id: str):
        if routine_id in self.memory["routines"]:
            self.memory["routines"][routine_id]["last_executed"] = datetime.now().isoformat()
            self.memory["routines"][routine_id]["execution_count"] += 1
            self.save()
    
    def get_due_routines(self) -> List[Dict]:
        due_routines = []
        now = datetime.now()
        
        for routine_id, routine in self.memory["routines"].items():
            if not routine.get("enabled", True):
                continue
            
            last_executed = routine.get("last_executed")
            frequency = routine.get("frequency", "daily")
            
            if last_executed is None:
                due_routines.append({**routine, "routine_id": routine_id})
                continue
            
            last_executed_dt = datetime.fromisoformat(last_executed)
            
            if frequency == "hourly" and (now - last_executed_dt) > timedelta(hours=1):
                due_routines.append({**routine, "routine_id": routine_id})
            elif frequency == "daily" and (now - last_executed_dt) > timedelta(days=1):
                due_routines.append({**routine, "routine_id": routine_id})
            elif frequency == "weekly" and (now - last_executed_dt) > timedelta(weeks=1):
                due_routines.append({**routine, "routine_id": routine_id})
        
        return due_routines
    
    def add_insight(self, insight: str, category: str = "general"):
        self.memory["insights"].append({
            "insight": insight,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 50 insights
        if len(self.memory["insights"]) > 50:
            self.memory["insights"] = self.memory["insights"][-50:]
        
        self.save()
    
    def get_tasks_requiring_followup(self, default_hours: int = 24) -> List[Dict]:
        followup_tasks = []
        now = datetime.now()
        
        for task_id, task in self.memory["tasks"].items():
            if task.get("status") == TaskStatus.WAITING_RESPONSE.value:
                last_action = task.get("last_action_time")
                if last_action:
                    last_action_dt = datetime.fromisoformat(last_action)
                    followup_after = task.get("followup_after_hours", default_hours)
                    
                    if (now - last_action_dt) > timedelta(hours=followup_after):
                        task["task_id"] = task_id
                        followup_tasks.append(task)
        
        return followup_tasks