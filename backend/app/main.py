from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import health, leads, integrations, webhook

# Create tables in SQLite on startup
Base.metadata.create_all(bind=engine)

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
