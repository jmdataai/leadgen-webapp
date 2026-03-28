from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class LeadSearchRequest(BaseModel):
    job_name: str
    job_titles: List[str]
    locations: List[str]
    company: Optional[str] = ""
    max_items: int = 10
    recipient_email: EmailStr
    workplace_type: Optional[List[str]] = []
    employment_type: Optional[List[str]] = []
    experience_level: Optional[List[str]] = []
    under_10_applicants: Optional[bool] = False
    easy_apply: Optional[bool] = False
    group_by_company: Optional[bool] = False
    leads_per_group: Optional[int] = 3

class JobResponse(BaseModel):
    id: int
    user_id: int
    job_name: str
    status: str
    search_params: Dict[str, Any]
    results_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
    id: int
    status: str
    results_count: int
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
