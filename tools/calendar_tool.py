import os
import datetime
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, ClassVar, List

class CalendarEventInput(BaseModel):
    summary: str = Field(description="Event title/summary")
    start_time: str = Field(description="Start time in format: YYYY-MM-DD HH:MM")
    end_time: str = Field(description="End time in format: YYYY-MM-DD HH:MM")
    description: Optional[str] = Field(default="", description="Event description")
    location: Optional[str] = Field(default="", description="Event location")
    attendees: Optional[str] = Field(default="", description="Comma-separated email addresses of attendees")

class GoogleCalendarTool(BaseTool):
    name: str = "Schedule Google Calendar Event"
    description: str = "Create a new event in Google Calendar"
    args_schema: Type[BaseModel] = CalendarEventInput
    
    SCOPES: ClassVar[List[str]] = ['https://www.googleapis.com/auth/calendar.events']
    
    def _authenticate_calendar(self):
        try:
            from tools.google_auth import get_google_credentials
            creds = get_google_credentials()
            if creds:
                return creds, None
            else:
                return None, "Calendar credentials not found. Please set up credentials.json"
        except Exception as e:
            return None, f"Authentication error: {str(e)}"
    
    def _parse_datetime(self, dt_str: str) -> str:
        try:
            dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            return dt.isoformat()
        except:
            return dt_str
    
    def _run(self, summary: str, start_time: str, end_time: str, 
             description: str = "", location: str = "", attendees: str = "") -> str:
        try:
            creds, error = self._authenticate_calendar()
            if error:
                return f"Error: {error}"
            
            service = build('calendar', 'v3', credentials=creds)
            
            event = {
                'summary': summary,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': self._parse_datetime(start_time),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': self._parse_datetime(end_time),
                    'timeZone': 'America/New_York',
                },
                'reminders': {
                    'useDefault': True,
                },
            }
            
            if attendees:
                attendee_list = [{'email': email.strip()} for email in attendees.split(',')]
                event['attendees'] = attendee_list
            
            event = service.events().insert(calendarId='primary', body=event).execute()
            
            return f"Event created successfully! Event link: {event.get('htmlLink')}"
            
        except Exception as e:
            return f"Error creating calendar event: {str(e)}"

class ListCalendarEventsInput(BaseModel):
    days_ahead: int = Field(default=7, description="Number of days ahead to check for events")

class ListCalendarEventsTool(BaseTool):
    name: str = "List Calendar Events"
    description: str = "List upcoming events from Google Calendar"
    args_schema: Type[BaseModel] = ListCalendarEventsInput
    
    SCOPES: ClassVar[List[str]] = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def _authenticate_calendar(self):
        try:
            from tools.google_auth import get_google_credentials
            creds = get_google_credentials()
            if creds:
                return creds, None
            else:
                return None, "Calendar credentials not found. Please set up credentials.json"
        except Exception as e:
            return None, f"Authentication error: {str(e)}"
    
    def _run(self, days_ahead: int = 7) -> str:
        try:
            creds, error = self._authenticate_calendar()
            if error:
                return f"Error: {error}"
            
            service = build('calendar', 'v3', credentials=creds)
            
            now = datetime.datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + datetime.timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return f"No upcoming events found in the next {days_ahead} days."
            
            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                event_list.append(f"- {start}: {summary}")
            
            return f"Upcoming events in the next {days_ahead} days:\n" + "\n".join(event_list)
            
        except Exception as e:
            return f"Error listing calendar events: {str(e)}"