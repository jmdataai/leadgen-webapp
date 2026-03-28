"""
Apify Service for LinkedIn Job Search
Uses harvestapi~linkedin-job-search actor
Production-ready with minimal logging
"""
import logging
from typing import Dict, List
from apify_client import ApifyClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class ApifyService:
    # Mapping from frontend values to Apify expected values
    WORKPLACE_TYPE_MAP = {
        "On-site": "office",
        "Remote": "remote",
        "Hybrid": "hybrid"
    }
    
    EMPLOYMENT_TYPE_MAP = {
        "Full-time": "full-time",
        "Part-time": "part-time",
        "Contract": "contract",
        "Internship": "intership",
        "Temporary": "temporary"
    }
    
    EXPERIENCE_LEVEL_MAP = {
        "Entry level": "entry",
        "Mid-Senior level": "mid-senior",
        "Associate": "associate",
        "Director": "director",
        "Executive": "executive",
        "Internship": "internship"
    }
    
    def __init__(self):
        api_key = settings.APIFY_API_KEY
        if not api_key:
            raise ValueError("APIFY_API_KEY not found in settings")
        
        self.client = ApifyClient(api_key)
        self.job_actor_id = settings.APIFY_JOB_ACTOR_ID
        self.employee_actor_id = settings.APIFY_EMPLOYEE_ACTOR_ID
        logger.info(f"Apify Service initialized - Job Actor: {self.job_actor_id}")
    
    def _map_workplace_types(self, workplace_types: List[str]) -> List[str]:
        """Map frontend workplace type values to Apify expected values"""
        if not workplace_types:
            return []
        
        mapped = []
        for wt in workplace_types:
            if wt in self.WORKPLACE_TYPE_MAP:
                mapped.append(self.WORKPLACE_TYPE_MAP[wt])
            else:
                mapped.append(wt.lower())
        
        return mapped
    
    def _map_employment_types(self, employment_types: List[str]) -> List[str]:
        """Map frontend employment type values to Apify expected values"""
        if not employment_types:
            return []
        
        mapped = []
        for et in employment_types:
            if et in self.EMPLOYMENT_TYPE_MAP:
                mapped.append(self.EMPLOYMENT_TYPE_MAP[et])
            else:
                mapped.append(et.lower())
        
        return mapped
    
    def _map_experience_levels(self, experience_levels: List[str]) -> List[str]:
        """Map frontend experience level values to Apify expected values"""
        if not experience_levels:
            return []
        
        mapped = []
        for el in experience_levels:
            if el in self.EXPERIENCE_LEVEL_MAP:
                mapped.append(self.EXPERIENCE_LEVEL_MAP[el])
            else:
                mapped.append(el.lower())
        
        return mapped
    
    def search_linkedin_jobs(self, search_params: Dict) -> List[Dict]:
        """Search LinkedIn jobs using Apify"""
        
        logger.info("Starting LinkedIn job search")
        
        run_input = {
            "jobTitles": search_params.get("job_titles", []),
            "locations": search_params.get("locations", []),
            "maxItems": search_params.get("max_items", 10),
            "sortBy": "date",
            "under10Applicants": bool(search_params.get("under_10_applicants", False)),
            "easyApply": bool(search_params.get("easy_apply", False))
        }
        
        company = search_params.get("company", "")
        if company:
            if isinstance(company, str):
                run_input["company"] = [comp.strip() for comp in company.split(',') if comp.strip()]
            else:
                run_input["company"] = company
        
        workplace_type = search_params.get("workplace_type", [])
        if workplace_type:
            run_input["workplaceType"] = self._map_workplace_types(workplace_type)
        
        employment_type = search_params.get("employment_type", [])
        if employment_type:
            run_input["employmentType"] = self._map_employment_types(employment_type)
        
        experience_level = search_params.get("experience_level", [])
        if experience_level:
            run_input["experienceLevel"] = self._map_experience_levels(experience_level)
        
        try:
            run = self.client.actor(self.job_actor_id).call(run_input=run_input)
            
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise Exception("No dataset ID returned from Apify")
            
            dataset_client = self.client.dataset(dataset_id)
            items = list(dataset_client.iterate_items())
            
            logger.info(f"Retrieved {len(items)} jobs from Apify")
            
            transformed_jobs = []
            for item in items:
                location_parsed = item.get("location", {}).get("parsed", {})
                apply_method = item.get("applyMethod", {})
                company_info = item.get("company", {})
                
                job = {
                    "title": item.get("title", ""),
                    "linkedin_url": item.get("linkedinUrl", ""),
                    "posted_date": item.get("postedDate", ""),
                    "description": item.get("descriptionText", ""),
                    "header": item.get("headerCaptionText", ""),
                    "country": location_parsed.get("countryFull", ""),
                    "state": location_parsed.get("state", ""),
                    "city": location_parsed.get("city", ""),
                    "employment_type": item.get("employmentType", ""),
                    "workplace_type": item.get("workplaceType", ""),
                    "easy_apply_url": apply_method.get("easyApplyUrl", ""),
                    "company": company_info.get("name", ""),
                    "company_website": company_info.get("website", ""),
                    "experience_level": item.get("experienceLevel", ""),
                    "job_url": apply_method.get("companyApplyUrl", ""),
                    "company_linked_url": company_info.get("linkedinUrl", ""),
                }
                transformed_jobs.append(job)
            
            return transformed_jobs
            
        except Exception as e:
            logger.error(f"Error in Apify job search: {str(e)}")
            raise
    
    def get_run_status(self, run_id: str) -> Dict:
        """Get status of a running Apify job"""
        status = self.client.run(run_id).get()
        return status
