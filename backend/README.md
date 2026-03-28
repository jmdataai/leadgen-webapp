---
title: LeadGen API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# LeadGen AI — FastAPI Backend

AI-powered lead generation API built with FastAPI + Python 3.9.

## API Endpoints
- `GET /` — API info
- `GET /api/health` — Health check  
- `POST /api/auth/register` — Register user
- `POST /api/auth/login` — Login
- `GET /docs` — Swagger UI (interactive API docs)

## Tech Stack
- FastAPI + Uvicorn
- SQLAlchemy ORM
- PostgreSQL (Supabase)
- OpenAI, Apify, Gmail integrations
