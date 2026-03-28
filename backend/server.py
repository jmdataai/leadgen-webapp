"""
AI Lead Generator - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.core.database import init_db
from app.api.endpoints import auth, leads

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting LeadGen AI API...")
    init_db()
    logger.info("LeadGen AI API ready!")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="AI Lead Generator",
    description="Intelligent lead generation system powered by AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
origins = CORS_ORIGINS.split(",") if CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])

@app.get("/")
async def root():
    return {
        "message": "AI Lead Generator API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Lead Generator",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )