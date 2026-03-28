"""
Lead Scraper Service using Apify LinkedIn Company Employees Scraper
Production-ready with minimal logging
"""
import logging
import pandas as pd
from typing import Dict, List
from apify_client import ApifyClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class LeadScraper:
    """LinkedIn Company Employees Scraper using Apify"""
    
    def __init__(self):
        api_key = settings.APIFY_API_KEY
        if not api_key:
            raise ValueError("APIFY_API_KEY not found")
        
        self.client = ApifyClient(api_key)
        self.actor_id = settings.APIFY_EMPLOYEE_ACTOR_ID
        logger.info(f"Lead Scraper initialized - Employee Actor: {self.actor_id}")
    
    def scrape_company_employees(
        self,
        company_urls: List[str],
        job_titles: List[str],
        locations: List[str],
        max_items_per_company: int = 1
    ) -> List[Dict]:
        """Scrape LinkedIn employees for companies"""
        
        logger.info(f"Scraping {len(company_urls)} companies for employees")
        
        formatted_titles = [f'"{title}"' for title in job_titles]
        
        run_input = {
            "companies": company_urls,
            "locations": locations,
            "jobTitles": formatted_titles,
            "maxItemsPerCompany": max_items_per_company,
            "profileScraperMode": "Short ($4 per 1k)",
            "recentlyChangedJobs": False,
            "takePages": 1,
            "companyBatchMode": "one_by_one"
        }
        
        try:
            run = self.client.actor(self.actor_id).call(run_input=run_input)

            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                logger.warning("No dataset returned from employee scraper")
                return []
            
            dataset_client = self.client.dataset(dataset_id)
            employees = list(dataset_client.iterate_items())
            
            logger.info(f"Found {len(employees)} employees")
            return employees
            
        except Exception as e:
            logger.error(f"Error scraping employees: {str(e)}")
            return []
    
    def enrich_jobs_with_employees(
        self,
        jobs: List[Dict],
        locations: List[str],
        max_employees_per_company: int = 1
    ) -> List[Dict]:
        """Enrich job listings with employee contact information"""
        
        logger.info(f"Enriching {len(jobs)} jobs with employee contacts")
        
        # Clean jobs data
        cleaned_jobs = []
        for job in jobs:
            cleaned_job = {}
            for key, value in job.items():
                if isinstance(value, list):
                    cleaned_job[key] = ','.join(str(v) for v in value)
                elif isinstance(value, dict):
                    cleaned_job[key] = str(value)
                else:
                    cleaned_job[key] = value
            cleaned_jobs.append(cleaned_job)
        
        df_jobs = pd.DataFrame(cleaned_jobs)
        
        if 'company' not in df_jobs.columns or 'company_linked_url' not in df_jobs.columns:
            logger.error("Missing required columns: company or company_linked_url")
            return jobs
        
        # Get unique companies
        unique_company_data = df_jobs[['company', 'company_linked_url']].drop_duplicates()
        unique_company_data = unique_company_data[
            unique_company_data['company_linked_url'].notna() & 
            (unique_company_data['company_linked_url'].str.strip() != '')
        ]
        
        company_linkedinurl_list = unique_company_data['company_linked_url'].tolist()
        
        if len(company_linkedinurl_list) == 0:
            logger.warning("No company LinkedIn URLs found")
            for job in jobs:
                job['recruiter_first_name'] = ''
                job['recruiter_last_name'] = ''
                job['recruiter_linkedin_url'] = ''
            return jobs
        
        # Scrape employees
        job_titles = ["HR Manager", "Talent Acquisition", "Recruiter", "People Operations"]
        
        employees = self.scrape_company_employees(
            company_urls=company_linkedinurl_list,
            job_titles=job_titles,
            locations=locations,
            max_items_per_company=max_employees_per_company
        )
        
        # Map employees by company URL from _meta.query.currentCompanies
        employee_map = {}
        
        for emp in employees:
            meta = emp.get('_meta', {})
            query = meta.get('query', {})
            current_companies = query.get('currentCompanies', [])
            
            if current_companies and len(current_companies) > 0:
                company_url = current_companies[0]
                normalized_url = company_url.rstrip('/').split('?')[0].split('#')[0]
                
                if normalized_url not in employee_map:
                    employee_map[normalized_url] = []
                
                employee_map[normalized_url].append(emp)
        
        # Enrich jobs
        enriched_jobs = []
        
        for _, job_row in df_jobs.iterrows():
            job = job_row.to_dict()
            
            company_url = str(job.get('company_linked_url', ''))
            normalized_job_url = company_url.rstrip('/').split('?')[0].split('#')[0]
            
            company_employees = employee_map.get(normalized_job_url, [])
            
            if company_employees:
                emp = company_employees[0]
                job['recruiter_first_name'] = emp.get('firstName', '')
                job['recruiter_last_name'] = emp.get('lastName', '')
                job['recruiter_linkedin_url'] = emp.get('linkedinUrl', '')
            else:
                job['recruiter_first_name'] = ''
                job['recruiter_last_name'] = ''
                job['recruiter_linkedin_url'] = ''
            
            enriched_jobs.append(job)
        
        contacts_found = sum(1 for j in enriched_jobs if j.get('recruiter_first_name', ''))
        logger.info(f"Enrichment complete: {contacts_found}/{len(jobs)} jobs with contacts")
        
        return enriched_jobs
