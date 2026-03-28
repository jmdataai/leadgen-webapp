# LeadGen AI — Web Application

AI-powered lead generation platform with LinkedIn scraping, OpenAI enrichment, and Gmail integration.

## Project Structure

```
leadgen-webapp/
├── backend/          ← FastAPI Python backend (deploys to HuggingFace)
│   ├── app/
│   │   ├── api/      ← API routes
│   │   ├── core/     ← Auth, DB, Config
│   │   ├── schemas/  ← Pydantic models
│   │   └── services/ ← OpenAI, Apify, Gmail
│   ├── server.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         ← React frontend (deploys to Vercel)
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── utils/
│   └── package.json
└── .github/
    └── workflows/
        └── hf_sync.yml  ← Auto-deploys backend to HuggingFace on push
```

## Deployments

| Part | Platform | URL |
|---|---|---|
| Backend API | HuggingFace Spaces | https://freddy-jmdataai-leadgen-api.hf.space |
| Frontend App | Vercel | https://leadgen-webapp.vercel.app |
| API Docs | HuggingFace | https://freddy-jmdataai-leadgen-api.hf.space/docs |

## Tech Stack

**Backend:** FastAPI, Uvicorn, SQLAlchemy, PostgreSQL (Supabase)  
**Frontend:** React, Craco, TailwindCSS, Axios  
**Integrations:** OpenAI (gpt-4o-mini), Apify (LinkedIn), Gmail OAuth2
