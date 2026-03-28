"""
AI Lead Generator - FastAPI Backend
Production-ready lead generation system
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.database import engine, Base
from app.api.endpoints import auth, leads

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Lead Generator",
    description="Intelligent lead generation system powered by AI",
    version="2.0.0"
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
origins = CORS_ORIGINS.split(",") if CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Lead Generator API",
        "version": "2.0.0",
        "status": "running"
    }

# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Lead Generator",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 AI LEAD GENERATOR - Starting Server")
    print("="*60)
    print(f"📍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🌐 URL: http://localhost:8001")
    print(f"📚 API Docs: http://localhost:8001/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
