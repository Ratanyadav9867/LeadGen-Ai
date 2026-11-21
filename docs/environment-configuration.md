# LeadGen AI — Environment Configuration Guide

This document details all configuration variables for the frontend, backend, Gemini AI, and automation pipelines.

---

## 🔒 Security Principles

1. **Zero Client Secrets**: Never insert API keys, service account JSONs, or email passwords in the frontend directory or `.env` files.
2. **Environment Isolation**: `.env` files are ignored in `.gitignore` and must never be committed into version control.
3. **Graceful Fallbacks**: If `GEMINI_API_KEY` is omitted or unconfigured, LeadGen AI automatically uses a deterministic rule-based qualification engine so local testing never breaks.

---

## 📄 Backend Configuration (`backend/.env`)

| Variable | Default Value | Description |
|---|---|---|
| `HOST` | `127.0.0.1` | Network interface for FastAPI to bind |
| `PORT` | `8000` | Port for ASGI web server |
| `ENVIRONMENT` | `development` | Runtime environment (`development`, `production`) |
| `DATABASE_URL` | `sqlite:///./leadgen.db` | SQLAlchemy connection string |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed origins for browser fetch requests |
| `GEMINI_API_KEY` | `""` | Google AI Studio Gemini API Key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model variant (`gemini-1.5-flash`, `gemini-2.5-flash`) |
| `N8N_WEBHOOK_URL` | `http://localhost:5678/webhook/leads` | Target n8n incoming webhook URL |
| `GOOGLE_SHEET_ID` | `""` | 44-character Google Sheet Document ID |
| `GMAIL_SENDER_ADDRESS` | `""` | Authenticated Google Workspace sender address |

### Sample `backend/.env`
```ini
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
DATABASE_URL=sqlite:///./leadgen.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Gemini API Key (Obtain from Google AI Studio: https://aistudio.google.com/)
GEMINI_API_KEY=AIzaSyD-your-verified-key-here
GEMINI_MODEL=gemini-1.5-flash

# Google Integrations
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GMAIL_SENDER_ADDRESS=admissions@example.com
N8N_WEBHOOK_URL=http://localhost:5678/webhook/leads
```

---

## 💻 Frontend Configuration (`frontend/.env`)

| Variable | Default Value | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend REST API base URL |

*(Note: In Vite development, requests to `/api` are also reverse-proxied by `vite.config.ts` to `http://127.0.0.1:8000` for zero CORS friction).*

