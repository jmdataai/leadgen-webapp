from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from app.core.database import get_db, User, Job
from app.core.auth import get_current_active_user
from app.schemas.leads import LeadSearchRequest, JobResponse, JobStatusResponse

router = APIRouter()

@router.post("/search", response_model=dict)
async def create_lead_search(
    search_request: LeadSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new lead search job"""
    
    print("\n" + "="*80)
    print("🎯 NEW LEAD SEARCH REQUEST RECEIVED")
    print("="*80)
    print(f"👤 User ID: {current_user.id}")
    print(f"📧 User Email: {current_user.email}")
    
    # Check daily limit
    from datetime import date
    today_jobs = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.created_at >= datetime.combine(date.today(), datetime.min.time())
    ).count()
    
    print(f"📊 Today's jobs: {today_jobs}/10")
    
    if today_jobs >= 10:  # MAX_JOBS_PER_USER_PER_DAY
        print(f"❌ Daily limit reached")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily job limit reached. Please try again tomorrow."
        )
    
    # Convert request to dict
    search_params = search_request.model_dump()
    
    print(f"\n📋 SEARCH REQUEST DETAILS:")
    print(f"   Job Name: {search_request.job_name}")
    print(f"   Job Titles: {search_request.job_titles}")
    print(f"   Locations: {search_request.locations}")
    print(f"   Company: {search_request.company or 'Any'}")
    print(f"   Max Items: {search_request.max_items}")
    print(f"   Recipient Email: {search_request.recipient_email}")
    print(f"   Workplace Type: {search_request.workplace_type}")
    print(f"   Employment Type: {search_request.employment_type}")
    print(f"   Experience Level: {search_request.experience_level}")
    print(f"   Under 10 Applicants: {search_request.under_10_applicants}")
    print(f"   Easy Apply: {search_request.easy_apply}")
    
    print(f"\n🔄 CONVERTING TO JSON FORMAT:")
    print(json.dumps(search_params, indent=2))
    
    # Create job record
    new_job = Job(
        user_id=current_user.id,
        job_name=search_request.job_name,
        status="pending",
        search_params=search_params,
        results_count=0
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    print(f"\n✅ JOB CREATED IN DATABASE")
    print(f"   Job ID: {new_job.id}")
    print(f"   Status: {new_job.status}")
    print(f"   Created At: {new_job.created_at}")
    
    # Add background task to process the job
    print(f"\n🚀 SCHEDULING BACKGROUND TASK")
    background_tasks.add_task(process_lead_job_with_logging, new_job.id)
    
    print(f"\n✅ REQUEST COMPLETED")
    print(f"   Response: Job {new_job.id} created successfully")
    print("="*80 + "\n")
    
    return {
        "message": "Job created successfully",
        "job_id": new_job.id,
        "status": "pending"
    }

@router.get("/history", response_model=List[JobResponse])
def get_job_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's job history"""
    
    print(f"\n📊 FETCHING JOB HISTORY")
    print(f"   User ID: {current_user.id}")
    
    jobs = db.query(Job).filter(
        Job.user_id == current_user.id
    ).order_by(Job.created_at.desc()).all()
    
    print(f"   Found {len(jobs)} jobs")
    
    return jobs

@router.get("/job/{job_id}", response_model=JobResponse)
def get_job_details(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific job details"""
    
    print(f"\n🔍 FETCHING JOB DETAILS")
    print(f"   Job ID: {job_id}")
    print(f"   User ID: {current_user.id}")
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        print(f"   ❌ Job not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    print(f"   ✅ Job found: {job.job_name}")
    print(f"   Status: {job.status}")
    
    return job

@router.get("/job/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get job status"""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {
        "id": job.id,
        "status": job.status,
        "results_count": job.results_count,
        "error_message": job.error_message
    }

@router.delete("/job/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a job"""
    
    print(f"\n🗑️  DELETING JOB")
    print(f"   Job ID: {job_id}")
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    db.delete(job)
    db.commit()
    
    print(f"   ✅ Job deleted successfully")
    
    return {"message": "Job deleted successfully"}

# Background task to process jobs
def process_lead_job_with_logging(job_id: int):
    """
    Process lead generation job in background
    WITH REAL APIFY/OPENAI INTEGRATION AND DEBUG LOGGING
    """
    
    print("\n" + "="*80)
    print(f"🔄 BACKGROUND TASK STARTED")
    print(f"   Job ID: {job_id}")
    print("="*80)
    print("208")
    
    try:
        # Import JobProcessor
        from app.services.job_processor import JobProcessor
        print("213")
        # Create processor instance
        processor = JobProcessor()
        print("216")
        # Process the job
        processor.process_job(job_id)
        
        print(f"\n✅ BACKGROUND TASK COMPLETED")
        print(f"   Job ID: {job_id}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ BACKGROUND TASK FAILED")
        print(f"   Job ID: {job_id}")
        print(f"   Error: {str(e)}")
        print("="*80 + "\n")
        
        # Update job status to failed
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

