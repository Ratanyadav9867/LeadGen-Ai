from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.database import engine, Base
import app.models
from app.routes import health, leads, integrations, webhook

# Create tables in SQLite on startup
Base.metadata.create_all(bind=engine)


def ensure_sqlite_columns():
    """Safely adds missing Phase 6 columns to existing SQLite tables."""
    try:
        with engine.connect() as conn:
            # Check leads columns
            res = conn.execute(text("PRAGMA table_info(leads)")).fetchall()
            lead_cols = [r[1] for r in res]
            if "gmail_message_id" not in lead_cols:
                conn.execute(text("ALTER TABLE leads ADD COLUMN gmail_message_id VARCHAR(100)"))
            if "error_message" not in lead_cols:
                conn.execute(text("ALTER TABLE leads ADD COLUMN error_message TEXT"))
            if "priority_source" not in lead_cols:
                conn.execute(text("ALTER TABLE leads ADD COLUMN priority_source VARCHAR(20) DEFAULT 'ai'"))

            # Check email_records columns
            res = conn.execute(text("PRAGMA table_info(email_records)")).fetchall()
            email_cols = [r[1] for r in res]
            if "gmail_message_id" not in email_cols:
                conn.execute(text("ALTER TABLE email_records ADD COLUMN gmail_message_id VARCHAR(100)"))
            if "error_message" not in email_cols:
                conn.execute(text("ALTER TABLE email_records ADD COLUMN error_message TEXT"))
            conn.commit()
    except Exception:
        pass


ensure_sqlite_columns()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LeadGen AI - Intelligent Lead Management & Automated Follow-Up System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "health": "/api/health",
        "leads": "/api/leads",
        "stats": "/api/leads/stats",
        "integrations": "/api/integrations/status",
        "emails": "/api/integrations/emails",
        "lead_capture": "/api/automation/lead-capture",
        "check_duplicate": "/api/leads/check-duplicate",
        "webhook": "/api/automation/webhook",
        "docs": "/docs"
    }
