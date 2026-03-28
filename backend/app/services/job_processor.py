"""
Main Job Processor - Orchestrates the entire workflow
Production-ready with minimal logging
"""
import logging
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List
from app.core.database import SessionLocal, Job
from app.services.apify_service import ApifyService
from app.services.openai_service import OpenAIService
from app.services.gmail_service import GmailService
from app.services.lead_scraper import LeadScraper

logger = logging.getLogger(__name__)


class JobProcessor:
    """Main workflow processor"""
    
    def __init__(self):
        print("23")
        self.apify = ApifyService()
        print("24")
        self.openai = OpenAIService()
        print("25")
        self.gmail = GmailService()
        print("26")
        self.scraper = LeadScraper()
        print("27")
        logger.info("Job Processor initialized")
    
    def process_job(self, job_id: int):
        """Complete workflow processing"""
        
        db = SessionLocal()
        
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            logger.info(f"Starting job processing - ID: {job_id}, Name: {job.job_name}")
            
            # Update status
            job.status = "processing"
            db.commit()
            
            search_params = job.search_params
            print("step1")
            # STEP 1: Apify Job Search
            logger.info("Step 1: Apify job search")
            jobs = self.apify.search_linkedin_jobs(search_params)
            
            if len(jobs) == 0:
                raise Exception("No jobs found matching criteria")
            
            logger.info(f"Found {len(jobs)} jobs")
            print("step2")
            # STEP 2: OpenAI Email Generation
            logger.info("Step 2: OpenAI email generation")
            jobs_with_emails = self.openai.batch_generate_emails(jobs)
            print("step3")
            # STEP 3: Lead Scraping
            logger.info("Step 3: Employee scraping")
            locations = search_params.get('locations', [])
            enriched_jobs = self.scraper.enrich_jobs_with_employees(
                jobs_with_emails,
                locations,
                max_employees_per_company=1
            )
            print("step4")
            # STEP 4: Create Reports
            logger.info("Step 4: Creating reports")
            csv_path, excel_path = self._create_reports(enriched_jobs, job.job_name)
            
            # STEP 5: Send Email
            logger.info("Step 5: Sending email")
            recipient_email = search_params.get('recipient_email', 'user@example.com')
            email_sent = self.gmail.send_lead_report(
                to=recipient_email,
                job_name=job.job_name,
                total_leads=len(enriched_jobs),
                excel_file_path=excel_path
            )
            
            if not email_sent:
                logger.warning("Email sending failed, but job completed successfully")
            
            # Update job with results
            job.status = "completed"
            job.results_count = len(enriched_jobs)
            job.results_data = {"leads": enriched_jobs}
            job.completed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Job {job_id} completed successfully - {len(enriched_jobs)} leads")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
            
        finally:
            db.close()
    
    def _create_reports(self, jobs: List[Dict], job_name: str) -> tuple:
        """
        Create CSV and Excel reports
        Returns: (csv_path, excel_path)
        """
        
        df = pd.DataFrame(jobs)
        
        output_data = []
        
        for _, row in df.iterrows():
            output_row = {
                'Title': row.get('title', ''),
                'Linkedin Url': row.get('linkedin_url', ''),
                'Posted Date': row.get('posted_date', ''),
                'Description': row.get('description', ''),
                'Header': row.get('header', ''),
                'Country': row.get('country', ''),
                'State': row.get('state', ''),
                'City': row.get('city', ''),
                'Employment Type': row.get('employment_type', ''),
                'Workplace Type': row.get('workplace_type', ''),
                'Easy Apply Url': row.get('easy_apply_url', ''),
                'Company': row.get('company', ''),
                'Company Website': row.get('company_website', ''),
                'Experience Level': row.get('experience_level', ''),
                'Job Function': '',
                'Job Url': row.get('job_url', ''),
                'Email Prepared': row.get('email_body', ''),
                'Subject': row.get('email_subject', ''),
                'Company Linkedin Url': row.get('company_linked_url', ''),
                'Recruiter First Name': row.get('recruiter_first_name', ''),
                'Recruiter Last Name': row.get('recruiter_last_name', ''),
                'Recruiter Linkedin Url': row.get('recruiter_linkedin_url', '')
            }
            
            output_data.append(output_row)
        
        df_output = pd.DataFrame(output_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_job_name = job_name.replace(' ', '_').replace('/', '_')
        
        os.makedirs('data/reports', exist_ok=True)
        
        # Save CSV
        csv_filename = f"Linkedin_Job_Postings_{safe_job_name}_{timestamp}.csv"
        csv_path = os.path.join("data/reports", csv_filename)
        df_output.to_csv(csv_path, index=False)
        
        # Save Excel
        excel_filename = f"Linkedin_Job_Postings_{safe_job_name}_{timestamp}.xlsx"
        excel_path = os.path.join("data/reports", excel_filename)
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_output.to_excel(writer, index=False, sheet_name='Job Applications')
            worksheet = writer.sheets['Job Applications']
            
            # Auto-adjust column widths
            for idx, col in enumerate(df_output.columns):
                max_length = max(
                    df_output[col].astype(str).apply(len).max(),
                    len(col)
                )
                col_letter = self._get_excel_column_letter(idx)
                worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)
        
        logger.info(f"Reports created - CSV: {csv_path}, Excel: {excel_path}")
        
        return csv_path, excel_path
    
    def _get_excel_column_letter(self, idx: int) -> str:
        """Convert column index to Excel letter"""
        letter = ""
        while idx >= 0:
            letter = chr(65 + (idx % 26)) + letter
            idx = idx // 26 - 1
        return letter

