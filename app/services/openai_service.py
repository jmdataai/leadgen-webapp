"""
OpenAI Service for Job Application Email Generation
Production-ready with minimal logging
"""
import logging
from typing import Dict, List
import httpx
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        
        if not api_key:
            logger.warning("OPENAI_API_KEY not found - will use generic application emails")
            self.client = None
            self.model = None
        else:
            # Create httpx client without proxy support to avoid the error
            http_client = httpx.Client(
                timeout=60.0,
                follow_redirects=True
            )
            self.client = OpenAI(api_key=api_key, http_client=http_client)
            self.model = settings.OPENAI_MODEL
            logger.info(f"OpenAI Service initialized - Model: {self.model}")
    
    def generate_email_subject(self, job_data: Dict) -> str:
        """Generate job application email subject line"""
        
        job_title = job_data.get('title', 'Position')
        company = job_data.get('company', 'Company')
        fallback_subject = f"Application for {job_title} Position"
        
        if not self.client:
            return fallback_subject
        
        prompt = f"""Generate a professional email subject line for a job application.

Job Details:
- Title: {job_data.get('title', 'N/A')}
- Company: {job_data.get('company', 'N/A')}
- Location: {job_data.get('location', 'N/A')}

Requirements:
- Keep it under 60 characters
- Professional and clear
- Should indicate this is a job application
- Include the job title

Return ONLY the subject line, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at writing professional job application emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            subject = response.choices[0].message.content.strip()
            subject = subject.strip('"\'')
            return subject
            
        except Exception as e:
            logger.error(f"OpenAI API error (subject): {str(e)}")
            return fallback_subject
    
    def generate_email_body(self, job_data: Dict, user_info: Dict = None) -> str:
        """Generate job application email body"""
        
        job_title = job_data.get('title', 'this position')
        company = job_data.get('company', 'your company')
        location = f"{job_data.get('city', '')}, {job_data.get('state', '')}".strip(', ')
        if not location:
            location = job_data.get('country', 'the location')
        
        employment_type = job_data.get('employment_type', 'N/A')
        experience_level = job_data.get('experience_level', 'N/A')
        linkedin_url = job_data.get('linkedin_url', '#')
        description = job_data.get('description', '')[:500]
        header = job_data.get('header', '')
        
        greeting = "Dear Hiring Manager"
        
        fallback_body = f"""{greeting},

I am writing to express my strong interest in the {job_title} position at {company}, as advertised on LinkedIn.

With my background and skills, I am confident that I would be a valuable addition to your team. The opportunity to work at {company} particularly excites me, and I believe my experience aligns well with the requirements for this role.

I have carefully reviewed the job description and am enthusiastic about the possibility of contributing to your organization. I am particularly drawn to this opportunity because of {company}'s reputation and the scope of responsibilities outlined for this position.

Key highlights of my qualifications:
- Strong professional background relevant to {job_title}
- Proven track record of delivering results
- Excellent communication and collaboration skills
- Passionate about continuous learning and growth

I would welcome the opportunity to discuss how my background, skills, and enthusiasm can contribute to {company}'s continued success. I am available for an interview at your convenience and can provide references upon request.

Thank you for considering my application. I look forward to the possibility of discussing this exciting opportunity with you.

Job Reference: {linkedin_url}

Best regards,
[Your Name]
[Your Contact Information]"""
        
        if not self.client:
            return fallback_body
        
        prompt = f"""Generate a professional job application email body.

Job Details:
- Title: {job_title}
- Company: {company}
- Location: {location}
- Employment Type: {employment_type}
- Experience Level: {experience_level}
- LinkedIn URL: {linkedin_url}

Context: {header}

Job Description Excerpt:
{description}

Requirements:
- Write from the perspective of a job applicant
- Professional and enthusiastic tone
- Express genuine interest in the position
- Highlight relevant qualifications
- Request an interview/next steps
- Include the job URL as a reference
- Keep it concise (250-350 words)
- Format with proper paragraphs
- End professionally with "Best regards" and placeholder for name/contact

Return ONLY the email body in plain text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at writing compelling job application emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            
            body = response.choices[0].message.content.strip()
            return body
            
        except Exception as e:
            logger.error(f"OpenAI API error (body): {str(e)}")
            return fallback_body
    
    def batch_generate_emails(self, jobs: List[Dict], user_info: Dict = None) -> List[Dict]:
        """Generate job application emails for multiple jobs"""
        
        logger.info(f"Generating emails for {len(jobs)} jobs")
        
        enriched_jobs = []
        for idx, job in enumerate(jobs, 1):
            try:
                subject = self.generate_email_subject(job)
                body = self.generate_email_body(job, user_info)
                
                enriched_job = job.copy()
                enriched_job['email_subject'] = subject
                enriched_job['email_body'] = body
                
                enriched_jobs.append(enriched_job)
                
            except Exception as e:
                logger.error(f"Error generating email for job {idx}: {str(e)}")
                enriched_job = job.copy()
                enriched_job['email_subject'] = f"Application for {job.get('title', 'Position')} Position"
                enriched_job['email_body'] = f"Dear Hiring Manager,\n\nI am writing to apply for the {job.get('title', 'position')} role at {job.get('company', 'your company')}.\n\nBest regards"
                enriched_jobs.append(enriched_job)
        
        logger.info(f"Generated {len(enriched_jobs)} application emails")
        return enriched_jobs
