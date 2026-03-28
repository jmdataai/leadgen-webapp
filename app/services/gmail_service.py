"""
Gmail Service using SMTP
Sends emails with Excel attachments
"""
import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from app.core.config import settings

logger = logging.getLogger(__name__)


class GmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.from_email = settings.EMAIL_FROM_ADDRESS
        self.gmail_app_password = settings.GMAIL_APP_PASSWORD
        
        if not self.gmail_app_password:
            logger.warning("GMAIL_APP_PASSWORD not configured - email sending will fail")
        
        logger.info(f"Gmail SMTP Service initialized - From: {self.from_email}")
    
    def send_lead_report(
        self,
        to: str,
        job_name: str,
        total_leads: int,
        excel_file_path: str
    ) -> bool:
        """
        Send lead generation report via Gmail SMTP
        
        Args:
            to: Recipient email address
            job_name: Name of the job search
            total_leads: Number of leads found
            excel_file_path: Path to Excel file to attach
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        
        if not self.gmail_app_password:
            logger.error("Cannot send email: GMAIL_APP_PASSWORD not configured")
            return False
        
        if not os.path.exists(excel_file_path):
            logger.error(f"Excel file not found: {excel_file_path}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = f"Lead Generation Report: {job_name}"
            
            # Email body
            body = f"""Hello,

Your lead generation job "{job_name}" has been completed successfully!

Summary:
- Total leads found: {total_leads}
- Report attached: {os.path.basename(excel_file_path)}

The attached Excel file contains:
- Job listings with details
- AI-generated application emails (subject + body)
- Recruiter contact information (when available)

You can use the email templates in the spreadsheet to reach out to recruiters directly.

Best regards,
AI Lead Generator
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach Excel file
            with open(excel_file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(excel_file_path)}',
            )
            
            msg.attach(part)
            
            # Send email via SMTP
            logger.info(f"Sending email to {to}")
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.from_email, self.gmail_app_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
