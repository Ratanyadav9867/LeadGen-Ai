# LeadGen AI 🚀

> **Autonomous Lead Management & Intelligent Follow-Up CRM System**  
> *Engineered for the AI Automation Internship Practical Assessment*

LeadGen AI is an end-to-end, production-ready lead intake and automated qualification ecosystem. It seamlessly bridges **Google Forms**, **Google Sheets**, and **Gmail** through **n8n workflow orchestration** and **Google Gemini AI**, backed by a robust **FastAPI & SQLite** backend and a modern **React + Vite + TypeScript + Tailwind CSS** SaaS CRM dashboard.

---

## 📑 Table of Contents
- [Project Architecture](#-project-architecture)
- [Tech Stack Overview](#-tech-stack-overview)
- [End-to-End Pipeline Workflow](#-end-to-end-pipeline-workflow)
- [Quickstart Guide (PowerShell on Windows)](#-quickstart-guide-powershell-on-windows)
- [FastAPI REST Endpoints](#-fastapi-rest-endpoints)
- [Comprehensive Documentation Suite](#-comprehensive-documentation-suite)
- [Automated Testing & Quality Verification](#-automated-testing--quality-verification)
- [Security Protocol](#-security-protocol)

---

## 🏛️ Project Architecture

```
LeadGen-AI/
├── frontend/                     # React 19 + Vite 8 + TypeScript + Tailwind CSS UI
│   ├── src/
│   │   ├── components/           # Header, Sidebar, Badges, Modals, EmptyState
│   │   ├── pages/                # Overview, Leads, Automation, EmailHistory, Settings
│   │   ├── services/             # API service layer (Health, Leads, Webhooks)
│   │   ├── data/                 # Explicitly labeled demonstration dataset
│   │   ├── types/                # TypeScript interface contracts
│   │   └── App.tsx               # Client-side router & layout root
│   ├── vite.config.ts            # Tailwind v4 plugin + API reverse proxy
│   └── package.json
├── backend/                      # Python 3.11 + FastAPI + SQLAlchemy 2.0
│   ├── app/
│   │   ├── models/               # SQLAlchemy ORM models (Lead)
│   │   ├── routes/               # API routes (health, leads, integrations, webhook)
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   ├── services/             # Gemini AI scoring & fallback qualification engine
│   │   ├── config.py             # SettingsConfigDict environment variables
│   │   ├── database.py           # SQLite connection pool & session dependency
│   │   └── main.py               # FastAPI entrypoint, tables creation, CORS
│   ├── tests/
│   │   ├── test_health.py        # Health endpoint unit tests
│   │   └── test_leads.py         # Lead CRUD, AI generation, webhook & deduplication tests
│   ├── requirements.txt          # Python dependencies
│   └── .env.example              # Backend environment template
├── automation/                   # n8n Automation Engine
│   ├── n8n_leadgen_workflow.json # Importable production n8n workflow
│   └── README.md                 # Workflow setup, node mapping & resilience guide
├── docs/                         # Detailed Assessment Documentation
│   ├── installation.md           # Step-by-step installation instructions
│   ├── environment-configuration.md # Environment variables and secrets guide
│   ├── google-api-setup.md       # Google Forms, Sheets, Drive, Gmail OAuth setup
│   ├── n8n-workflow-setup.md     # n8n import, credentials and trigger instructions
│   ├── testing-guide.md          # Automated & manual test execution procedures
│   └── demo-script.md            # Three-minute assessment video recording script
├── scripts/                      # Verification and diagnostics scripts
│   └── verify_health_live.ps1    # Live FastAPI server & health verification script
├── .env.example                  # Root environment template
├── .gitignore                    # Excludes venv/, node_modules/, dist/, .env, *.db
└── README.md                     # Master documentation
```

---

## ⚙️ Tech Stack Overview

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **OS** | Windows 11/10 | Native PowerShell | Development and execution host |
| **Frontend** | React + Vite + TypeScript | React 19.3 / Vite 8.3 | High-performance SaaS CRM dashboard |
| **Styling** | Tailwind CSS | 4.3.5 | Modern utility-first CSS |
| **Icons** | Lucide React | 1.77.0 | Clean iconography |
| **Backend** | Python + FastAPI | Python 3.11 / FastAPI 0.165 | Asynchronous RESTful API engine |
| **Validation** | Pydantic v2 | 2.14.4 | Strict schema validation and typed configs |
| **Database** | SQLAlchemy 2.0 + SQLite | 2.1.9 | Persistent local relational storage |
| **AI Engine** | Google Gemini API | `gemini-1.5-flash` | Lead qualification, scoring & email drafting |
| **Automation** | n8n | v1 workflow schema | Multi-node pipeline orchestration |
| **Google Workspace** | Forms, Sheets, Gmail | v4 / OAuth2 | Inbound capture, logging, and Gmail OAuth dispatch (Phase 6) |
| **Testing** | Pytest & HTTPX | Pytest 9.2 / HTTPX 0.28 | Automated backend integration test suite (36 passing tests) |


---

## 🔄 End-to-End Pipeline Workflow

```
[Inbound Prospect fills Google Form]
               │
               ▼
[Row automatically appended to Google Sheets]
               │
               ▼
[n8n Google Sheets Trigger fires]
               │
               ▼
[n8n validates lead data & verifies duplicate status]
               │
               ▼
[n8n dispatches payload to FastAPI Webhook: POST /api/automation/webhook]
               │
               ▼
[FastAPI queries Google Gemini AI (gemini-1.5-flash)]
├── Analyzes project requirements & budget
├── Evaluates commercial priority: High / Medium / Low
├── Explains priority reasoning
└── Drafts customized, professional business follow-up email
               │
               ▼
[LeadGen AI persists record in SQLite database]
               │
               ▼
[n8n Gmail Node sends tailored follow-up to prospect]
               │
               ▼
[n8n Google Sheets Node logs: Status = 'Sent', AI Priority, Timestamp]
               │
               ▼
[CRM Dashboard immediately reflects new qualified lead]
```

---

## 🚀 Quickstart Guide (PowerShell on Windows)

### 1. Backend Server Setup & Start
Open a PowerShell terminal:
```powershell
# Navigate to backend
cd backend

# Create virtual environment (Python 3.11)
& "C:\Users\R\AppData\Local\Programs\Python\Python311\python.exe" -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Frontend CRM Dashboard Setup & Start
Open a second PowerShell terminal:
```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- CRM Dashboard: [http://localhost:5173](http://localhost:5173)

---

## 🔌 FastAPI REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Live system health and SQLite connection check |
| `GET` | `/api/leads` | List leads (supports `priority`, `email_status`, `search` query parameters) |
| `POST` | `/api/leads` | Create an inbound lead with automatic AI scoring |
| `GET` | `/api/leads/stats` | Pipeline metrics (Total, New, Contacted, High Priority, Failed) |
| `GET` | `/api/leads/{id}` | Retrieve comprehensive lead profile and AI email draft |
| `POST` | `/api/leads/{id}/generate-ai` | On-demand Google Gemini AI re-scoring and email synthesis |
| `PATCH` | `/api/leads/{id}/status` | Update email delivery status (`Pending`, `Sent`, `Failed`) or priority |
| `DELETE`| `/api/leads/{id}` | Remove lead record |
| `POST` | `/api/automation/webhook` | Webhook ingestion endpoint for n8n/Google Sheets with duplicate prevention |
| `GET` | `/api/integrations/status`| Live audit of environment variable configuration status |
| `GET` | `/api/integrations/emails`| Outreach log of generated and sent emails |

---

## 📚 Comprehensive Documentation Suite

- 📖 **[Installation Guide](docs/installation.md)**: Full local setup walkthrough for Windows.
- ⚙️ **[Environment Configuration Guide](docs/environment-configuration.md)**: Details on all `.env` options and Gemini model configuration.
- 🤖 **[Google Gemini AI Integration Guide](docs/GEMINI_SETUP.md)**: AI Studio key setup, prompt guardrails, and structured output.
- ✉️ **[Gmail OAuth & Email Delivery Guide](docs/GMAIL_SETUP.md)**: Gmail API OAuth setup, duplicate-send protection, and error handling.
- 🌐 **[Google APIs & Workspace Guide](docs/google-api-setup.md)**: Setting up Google Forms, Google Sheets headers, and Google Cloud OAuth credentials.
- 🔄 **[n8n Workflow Setup Guide](docs/n8n-workflow-setup.md)**: How to import `automation/workflows/lead-capture-workflow.json` and configure nodes.
- 🧪 **[End-to-End Testing & Verification Report](docs/END_TO_END_TESTING.md)**: Full integration verification and 46 automated test results.
- 🎬 **[Assessment Video Demonstration Script](docs/demo-script.md)**: Scene-by-scene script for assessment presentation.

---

## 🧪 Automated Testing & Quality Verification

### 1. Run Complete Backend Pytest Suite (46 Tests)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```
*(Result: 46 passing integration tests verifying health, lead CRUD, Gemini AI personalization, Gmail OAuth delivery, duplicate prevention, and end-to-end pipeline synchronization).*

### 2. Verify Frontend Production Build
```powershell
cd frontend
npm run build
```
*(Result: Zero TypeScript or bundling diagnostics; clean production build ready).*

### 3. Live Server Round-Trip Health Check
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_health_live.ps1
```

---

## 🛡️ Security Protocol

- **Zero Client Secrets**: No API keys or credentials exist in the client JavaScript bundle.
- **Server-Side Isolation**: Google Gemini API key and webhook targets reside exclusively on the server (`backend/.env`).
- **Input Sanitization**: Pydantic validates email formats and mandatory string boundaries on every API payload.
- **CORS Hardening**: FastAPI strictly permits requests from designated origins (`http://localhost:5173`).
