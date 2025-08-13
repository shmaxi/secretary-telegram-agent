import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, ClassVar, List

class GmailToolInput(BaseModel):
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body content")

class GmailTool(BaseTool):
    name: str = "Send Gmail"
    description: str = "Send an email using Gmail API"
    args_schema: Type[BaseModel] = GmailToolInput
    
    SCOPES: ClassVar[List[str]] = ['https://www.googleapis.com/auth/gmail.send']
    
    def _authenticate_gmail(self):
        try:
            from tools.google_auth import get_google_credentials
            creds = get_google_credentials()
            if creds:
                return creds, None
            else:
                return None, "Gmail credentials not found. Please set up credentials.json"
        except Exception as e:
            return None, f"Authentication error: {str(e)}"
    
    def _run(self, to: str, subject: str, body: str) -> str:
        try:
            creds, error = self._authenticate_gmail()
            if error:
                return f"Error: {error}"
            
            service = build('gmail', 'v1', credentials=creds)
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            message_body = {'raw': raw}
            
            sent_message = service.users().messages().send(
                userId='me', body=message_body).execute()
            
            return f"Email sent successfully! Message ID: {sent_message['id']}"
            
        except Exception as e:
            return f"Error sending email: {str(e)}"