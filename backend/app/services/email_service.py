"""
Email Service using Resend API
Sends emails with Excel attachments
Free tier: 3,000 emails/month, 100/day
Sign up at: https://resend.com
"""
import logging
import os
import base64
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    logger.warning("resend package not installed - run: pip install resend")


class EmailService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"

        if not self.api_key:
            logger.warning("RESEND_API_KEY not configured - email sending will fail")
        elif RESEND_AVAILABLE:
            resend.api_key = self.api_key
            logger.info(f"Resend Email Service initialized - From: {self.from_email}")

    def send_lead_report(
        self,
        to: str,
        job_name: str,
        total_leads: int,
        excel_file_path: str
    ) -> bool:
        """
        Send lead generation report via Resend API

        Args:
            to: Recipient email address
            job_name: Name of the job search
            total_leads: Number of leads found
            excel_file_path: Path to Excel file to attach

        Returns:
            bool: True if email sent successfully, False otherwise
        """

        if not self.api_key:
            logger.error("Cannot send email: RESEND_API_KEY not configured")
            return False

        if not RESEND_AVAILABLE:
            logger.error("Cannot send email: resend package not installed")
            return False

        if not os.path.exists(excel_file_path):
            logger.error(f"Excel file not found: {excel_file_path}")
            return False

        try:
            filename = os.path.basename(excel_file_path)

            # Read and encode attachment as base64
            with open(excel_file_path, 'rb') as f:
                file_content = base64.b64encode(f.read()).decode('utf-8')

            # HTML email body
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 30px; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">
                        LeadGen AI Report
                    </h1>
                </div>
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;
                            border: 1px solid #e0e0e0;">
                    <p style="color: #333; font-size: 16px;">Hello,</p>
                    <p style="color: #333;">
                        Your lead generation job <strong>"{job_name}"</strong>
                        has been completed successfully!
                    </p>
                    <div style="background: white; border-radius: 8px; padding: 20px;
                                border-left: 4px solid #667eea; margin: 20px 0;">
                        <h3 style="color: #667eea; margin: 0 0 12px 0;">Summary</h3>
                        <p style="margin: 6px 0; color: #555;">
                            Total leads found: <strong>{total_leads}</strong>
                        </p>
                        <p style="margin: 6px 0; color: #555;">
                            Report file: <strong>{filename}</strong>
                        </p>
                    </div>
                    <p style="color: #555;">The attached Excel file contains:</p>
                    <ul style="color: #555; line-height: 1.8;">
                        <li>Job listings with full details</li>
                        <li>AI-generated application emails (subject + body)</li>
                        <li>Recruiter contact information (when available)</li>
                    </ul>
                    <p style="color: #555;">
                        You can use the email templates in the spreadsheet to reach out
                        to recruiters directly.
                    </p>
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">
                    <p style="color: #999; font-size: 13px; margin: 0;">
                        Best regards,<br>
                        <strong>LeadGen AI</strong>
                    </p>
                </div>
            </div>
            """

            # Plain text fallback
            text_body = f"""Hello,

Your lead generation job "{job_name}" has been completed successfully!

Summary:
- Total leads found: {total_leads}
- Report attached: {filename}

The attached Excel file contains:
- Job listings with details
- AI-generated application emails (subject + body)
- Recruiter contact information (when available)

Best regards,
LeadGen AI
"""

            logger.info(f"Sending email to {to} via Resend")

            params = {
                "from": self.from_email,
                "to": [to],
                "subject": f"Lead Generation Report: {job_name}",
                "html": html_body,
                "text": text_body,
                "attachments": [
                    {
                        "filename": filename,
                        "content": file_content,
                    }
                ],
            }

            response = resend.Emails.send(params)

            if response and response.get("id"):
                logger.info(f"Email sent successfully to {to} — ID: {response['id']}")
                return True
            else:
                logger.error(f"Resend returned unexpected response: {response}")
                return False

        except Exception as e:
            logger.error(f"Failed to send email via Resend: {str(e)}")
            return False


# Keep old name as alias so nothing else in the codebase breaks
GmailService = EmailService
