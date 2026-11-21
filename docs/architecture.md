# LeadGen AI Architecture

## Overview
LeadGen AI is an AI-powered Lead Management and Automated Follow-Up CRM application designed to ingest leads from Google Forms/Sheets, store and qualify them in a FastAPI backend with SQLite, score and draft personalized follow-ups using Google Gemini AI, and trigger automated follow-up sequences through n8n and Gmail.

## Monorepo Structure
```
LeadGen-AI/
  ├── frontend/       # React + Vite + TypeScript + Tailwind CSS + Lucide React
  ├── backend/        # FastAPI + SQLAlchemy + SQLite + Pydantic
  ├── automation/     # n8n workflows and webhook documentation
  ├── docs/           # System design, API specs, deployment guides
  ├── .env.example    # Root environment variable template
  ├── .gitignore      # Monorepo gitignore
  └── README.md       # Project setup and execution guide
```

## Communication Flow
1. **Frontend**: Calls `/api/health` and future CRM endpoints on FastAPI (`http://127.0.0.1:8000`).
2. **Backend**: Handles business logic, SQLite persistence, and Gemini prompt orchestration.
3. **n8n Automation**: Dispatches webhooks to backend and orchestrates Google Workspace integrations.

