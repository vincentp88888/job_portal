import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class GmailHandler:
    def __init__(self):
        self.drafts_folder = "email_drafts"
        os.makedirs(self.drafts_folder, exist_ok=True)
    
    def create_draft_with_attachments(self, to: str, subject: str, body: str, attachments: list = []):
        msg = MIMEMultipart()
        msg['From'] = 'no-reply@example.com'
        msg['To'] = to
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        msg.attach(MIMEText(body, 'plain'))

        for file_path in attachments:
            if file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(file_path)}"'
                    )
                    msg.attach(part)

        safe_name = to.replace('@', '_at_').replace('.', '_')[:30]
        filename = f"draft_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
        filepath = os.path.join(self.drafts_folder, filename)

        with open(filepath, 'wb') as f:
            f.write(msg.as_bytes())

        return os.path.abspath(filepath)
