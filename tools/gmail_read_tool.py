import os
import base64
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, ClassVar, List

class GmailReadInput(BaseModel):
    query: Optional[str] = Field(default="is:unread", description="Gmail search query (e.g., 'is:unread', 'from:user@example.com', 'subject:meeting')")
    max_results: Optional[int] = Field(default=10, description="Maximum number of emails to retrieve")
    
class GmailReadTool(BaseTool):
    name: str = "Read Gmail"
    description: str = "Read emails from Gmail inbox using search queries"
    args_schema: Type[BaseModel] = GmailReadInput
    
    def _authenticate_gmail(self):
        try:
            from tools.google_auth import get_google_credentials
            # Use unified authentication with all scopes
            creds = get_google_credentials()
            if creds:
                return creds, None
            else:
                return None, "Gmail credentials not found. Please set up credentials.json"
        except Exception as e:
            return None, f"Authentication error: {str(e)}"
    
    def _run(self, query: str = "is:unread", max_results: int = 10) -> str:
        try:
            creds, error = self._authenticate_gmail()
            if error:
                return f"Error: {error}"
            
            service = build('gmail', 'v1', credentials=creds)
            
            # Search for messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return f"No emails found matching query: {query}"
            
            email_summaries = []
            
            for msg in messages:
                # Get the full message
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                # Extract headers
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                
                # Extract body
                body = self._extract_body(message['payload'])
                
                # Create summary
                email_summaries.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'snippet': message.get('snippet', '')[:200],  # First 200 chars
                    'body': body[:500] if body else 'No text content'  # First 500 chars of body
                })
            
            # Format the output
            output = f"Found {len(email_summaries)} email(s) matching '{query}':\n\n"
            
            for i, email in enumerate(email_summaries, 1):
                output += f"{i}. From: {email['from']}\n"
                output += f"   Subject: {email['subject']}\n"
                output += f"   Date: {email['date']}\n"
                output += f"   Preview: {email['snippet']}\n"
                output += f"   Body: {email['body']}\n"
                output += "-" * 50 + "\n"
            
            return output
            
        except Exception as e:
            return f"Error reading emails: {str(e)}"
    
    def _extract_body(self, payload):
        """Extract the email body from the payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
                elif 'parts' in part:
                    # Nested parts
                    body = self._extract_body(part)
                    if body:
                        break
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        
        return body

class CheckEmailResponsesInput(BaseModel):
    email_addresses: str = Field(description="Comma-separated list of email addresses to check responses from")
    subject_keyword: Optional[str] = Field(default="", description="Keyword to search in subject line")
    since_hours: Optional[int] = Field(default=24, description="Check emails from the last N hours")

class CheckEmailResponsesTool(BaseTool):
    name: str = "Check Email Responses"
    description: str = "Check if specific people have responded to emails"
    args_schema: Type[BaseModel] = CheckEmailResponsesInput
    
    def _authenticate_gmail(self):
        try:
            from tools.google_auth import get_google_credentials
            # Use unified authentication with all scopes
            creds = get_google_credentials()
            if creds:
                return creds, None
            else:
                return None, "Gmail credentials not found. Please set up credentials.json"
        except Exception as e:
            return None, f"Authentication error: {str(e)}"
    
    def _run(self, email_addresses: str, subject_keyword: str = "", since_hours: int = 24) -> str:
        try:
            creds, error = self._authenticate_gmail()
            if error:
                return f"Error: {error}"
            
            service = build('gmail', 'v1', credentials=creds)
            
            # Parse email addresses
            addresses = [addr.strip() for addr in email_addresses.split(',')]
            
            # Calculate date for query
            since_date = (datetime.now() - timedelta(hours=since_hours)).strftime('%Y/%m/%d')
            
            responses = {}
            
            for address in addresses:
                # Build query
                query = f"from:{address} after:{since_date}"
                if subject_keyword:
                    query += f" subject:{subject_keyword}"
                
                # Search for messages
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=5
                ).execute()
                
                messages = results.get('messages', [])
                
                if messages:
                    # Get details of the most recent message
                    latest = service.users().messages().get(
                        userId='me',
                        id=messages[0]['id']
                    ).execute()
                    
                    headers = latest['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                    
                    responses[address] = {
                        'responded': True,
                        'count': len(messages),
                        'latest_subject': subject,
                        'latest_date': date
                    }
                else:
                    responses[address] = {
                        'responded': False,
                        'count': 0
                    }
            
            # Format output
            output = f"Email Response Status (last {since_hours} hours):\n\n"
            
            responded = []
            not_responded = []
            
            for addr, info in responses.items():
                if info['responded']:
                    responded.append(f"✅ {addr}: {info['count']} email(s) - Latest: {info['latest_subject']} ({info['latest_date']})")
                else:
                    not_responded.append(f"❌ {addr}: No response yet")
            
            if responded:
                output += "Responded:\n" + "\n".join(responded) + "\n\n"
            
            if not_responded:
                output += "Awaiting Response:\n" + "\n".join(not_responded) + "\n\n"
                output += f"Consider sending a follow-up to: {', '.join([addr for addr, info in responses.items() if not info['responded']])}"
            
            return output
            
        except Exception as e:
            return f"Error checking email responses: {str(e)}"