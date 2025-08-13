import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import Optional, List

# All scopes needed for the secretary
ALL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def get_google_credentials(scopes: Optional[List[str]] = None) -> Optional[Credentials]:
    """
    Get or refresh Google credentials with all necessary scopes
    """
    if scopes is None:
        scopes = ALL_SCOPES
    
    creds = None
    token_path = 'google_token.pickle'
    
    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                # If refresh fails, re-authenticate
                creds = None
        
        if not creds:
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            if not os.path.exists(credentials_path):
                print(f"❌ Google credentials file not found: {credentials_path}")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, ALL_SCOPES)
            
            print("🔐 Opening browser for Google authentication...")
            print("Please authorize access to Gmail AND Calendar")
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Google authentication successful!")
    
    return creds