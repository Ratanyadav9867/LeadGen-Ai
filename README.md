# LeadGen AI 🚀

> **AI-Powered Lead Management & Automated Follow-Up CRM**  
> *Developed for the AI Automation Internship Assessment*

LeadGen AI is an autonomous CRM application designed to streamline lead capture, AI qualification/scoring, and intelligent automated follow-ups across Google Workspace (Google Forms, Google Sheets, Gmail) and n8n orchestration.

---

## 🏛️ Monorepo Architecture

```
LeadGen-AI/
├── frontend/                 # React + Vite + TypeScript + Tailwind CSS UI
│   ├── src/
│   │   ├── components/       # Header, Sidebar, HealthCard, UI components
│   │   ├── services/         # API client & health check service
│   │   ├── types/            # TypeScript data contracts & models
│   │   ├── App.tsx           # Dashboard layout & live health monitor
│   │   ├── index.css         # Tailwind CSS styling
│   │   └── main.tsx          # React application root
│   ├── vite.config.ts        # Vite configuration + API reverse proxy
│   └── package.json
├── backend/                  # FastAPI + SQLite + SQLAlchemy API
│   ├── app/
│   │   ├── models/           # SQLAlchemy ORM models (Base established)
│   │   ├── routes/           # REST API endpoints (/api/health)
│   │   ├── schemas/          # Pydantic validation schemas (HealthResponse)
│   │   ├── services/         # Business logic layer
│   │   ├── config.py         # Application settings via Pydantic Settings
│   │   ├── database.py       # SQLite engine & SessionLocal dependency
│   │   └── main.py           # FastAPI entrypoint & CORS middleware
│   ├── tests/
│   │   └── test_health.py    # Pytest health & root endpoint tests
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Backend environment variables
├── automation/               # n8n workflows & webhook documentation
│   └── README.md
├── docs/                     # Architecture & technical documentation
│   └── architecture.md
├── scripts/                  # Automation & verification scripts
│   └── verify_health_live.ps1 # Live health check verification script
├── .env.example              # Root environment variable template
├── .gitignore                # Exclusion rules (secrets, venv, build artifacts)
└── README.md                 # Project documentation & instructions
```

---

## ⚙️ Tech Stack & Environment

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **OS** | Microsoft Windows | Windows 11/10 | Host development environment |
| **Frontend Framework** | React + TypeScript | React 19.3.1 | Responsive SPA CRM dashboard |
| **Build Tool** | Vite | 8.3.8 | High-speed ESM development server & bundler |
| **Styling** | Tailwind CSS | 4.3.5 | Modern utility-first CSS framework |
| **Icons** | Lucide React | 1.77.0 | Clean iconography |
| **Backend Framework** | FastAPI | 0.165.0 | Async Python REST API |
| **Language Runtime** | Python | 3.11.9 | Stable Python runtime |
| **Data Validation** | Pydantic & Pydantic-Settings | 2.14.4 / 2.16.3 | Schema definitions & typed configs |
| **ORM & Database** | SQLAlchemy | 2.1.9 / SQLite | Relational database persistence |
| **ASGI Server** | Uvicorn | 0.54.0 | High-performance ASGI web server |
| **Testing** | Pytest & HTTPX | 9.2.0 / 0.28.1 | Automated API test suite |
| **Automation & AI** | n8n & Google Gemini API | Phase 2 & 3 | Workflow automation & lead qualification |

---

## 🚀 Quickstart Guide

### Prerequisites
- **Node.js** (v24.x recommended, verified on v24.20.0)
- **npm** (v11.x+, verified on 11.19.0)
- **Python 3.11** (located at `C:\Users\R\AppData\Local\Programs\Python\Python311\python.exe`)
- **Git** (verified on v2.56.0)

---

### 1. Backend Setup & Run

The backend can be run independently using its dedicated virtual environment:

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
& "C:\Users\R\AppData\Local\Programs\Python\Python311\python.exe" -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run FastAPI development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Backend API URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Health Endpoint**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 2. Frontend Setup & Run

The frontend runs independently with Vite dev server and proxy support:

```powershell
# Navigate to frontend directory
cd frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```

- **Frontend App URL**: [http://localhost:5173](http://localhost:5173)

---

### 3. Running Automated Tests

#### Backend Pytest Suite
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest -v
```

#### Frontend Build Verification
```powershell
cd frontend
npm run build
```

#### Live End-to-End Health Verification
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_health_live.ps1
```

---

## 🔍 Health Endpoint Output

`GET /api/health` response:
```json
{
  "status": "healthy",
  "service": "LeadGen AI",
  "version": "0.1.0",
  "environment": "development",
  "database": "connected"
}
```

---

## 🗺️ Project Roadmap

- [x] **Phase 1: Environment Inspection & Project Foundation** *(Completed)*
  - Monorepo directory structure
  - React + Vite + TypeScript + Tailwind CSS v4 frontend
  - FastAPI + SQLAlchemy + SQLite backend environment
  - Live `/api/health` connectivity and test validation
  - Environment templates (`.env.example`) and `.gitignore`
- [x] **Phase 2: CRM Dashboard UI & Core Lead Management** *(Completed)*
  - Modern SaaS CRM dashboard layout with Dark Navy Sidebar & light workspace
  - Executive Overview page with 5 KPI summary cards
  - Real-time Lead Management Table (Search, Filters, Sort, Modal inspection)
  - "High Priority Leads" dedicated view
  - Automation page with 6-stage pipeline visualization & genuine status checks
  - Automated Email History with preview dialog
  - System Settings with zero-client-secrets security adherence
  - FastAPI `/api/leads`, `/api/leads/stats`, and `/api/integrations` routes
- [ ] **Phase 3: Google Gemini AI Scoring & Qualification Engine**
  - Prompt engineering for lead qualification & urgency classification
  - Automated follow-up email draft generation
- [ ] **Phase 4: n8n Automation & Google Workspace Integration**
  - Ingestion webhook from Google Forms / Google Sheets
  - Automated Gmail notification and follow-up dispatch

