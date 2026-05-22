import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class GmailHandler:
    """
    Simple email draft creator - NO OAuth needed
    Saves drafts as .eml files you can open in any email client
    """
    
    def __init__(self):
        """Initialize - no authentication needed"""
        self.drafts_folder = "email_drafts"
        os.makedirs(self.drafts_folder, exist_ok=True)
        print(f"✅ Email drafts will be saved to: {self.drafts_folder}/")
    
    def create_draft_with_attachments(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: list = []
    ):
        """
        Create email draft as .eml file
        
        You can:
        1. Double-click the .eml file to open in Outlook/Mail/Thunderbird
        2. Drag it into Gmail
        3. Import it into any email client
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
        
        Returns:
            Path to saved .eml file
        """
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = 'your.email@gmail.com'  # Will be replaced when you send
        msg['To'] = to
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        for file_path in attachments:
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(file_path)}'
                        )
                        msg.attach(part)
                    print(f"  ✅ Attached: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"  ⚠️ Could not attach {file_path}: {e}")
        
        # Create safe filename
        safe_company = to.split('@')[:30].replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"draft_{safe_company}_{timestamp}.eml"
        filepath = os.path.join(self.drafts_folder, filename)
        
        # Save as .eml file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(msg.as_string())
        
        print(f"\n✅ Email draft saved: {filepath}")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")
        print(f"   Attachments: {len(attachments)}")
        
        return filepath
    
    def list_drafts(self):
        """List all saved draft files"""
        drafts = []
        if os.path.exists(self.drafts_folder):
            for filename in os.listdir(self.drafts_folder):
                if filename.endswith('.eml'):
                    filepath = os.path.join(self.drafts_folder, filename)
                    drafts.append({
                        'filename': filename,
                        'path': filepath,
                        'created': datetime.fromtimestamp(os.path.getctime(filepath))
                    })
        return drafts
