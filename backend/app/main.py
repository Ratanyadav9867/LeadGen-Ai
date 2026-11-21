from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import health, leads, integrations

# Create tables in SQLite on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LeadGen AI - AI-powered Lead Management & Automated Follow-Up CRM",
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


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "health": "/api/health",
        "leads": "/api/leads",
        "stats": "/api/leads/stats",
        "integrations": "/api/integrations/status",
        "emails": "/api/integrations/emails",
        "docs": "/docs"
    }
