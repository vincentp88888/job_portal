from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

class GmailHandler:
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def create_draft_with_attachments(self, to, subject, body, attachments=[]):
        """Create Gmail draft with attachments"""
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        for file_path in attachments:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(file_path)}'
                )
                message.attach(part)
        
        # Create draft
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft = {
            'message': {
                'raw': raw_message
            }
        }
        
        draft = self.service.users().drafts().create(
            userId='me',
            body=draft
        ).execute()
        
        return draft['id']
    
    def list_drafts(self):
        """List all drafts"""
        results = self.service.users().drafts().list(userId='me').execute()
        return results.get('drafts', [])
