from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
from datetime import datetime
import time
from typing import List, Dict, Any

from core.agents.supervisor_agent import RunningCoachSupervisor
from models import (
    AgenticAnalysis, AnalysisResponse, WorkoutFeedbackResponse,
    WorkoutData, WorkoutInsights, RunnerProfile
)
from utils.config import get_settings
from utils.logger import setup_logging
from utils.auth import get_supabase_auth

# Setup
settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI(
    title="Runaway Coach API",
    description="AI-powered running coach using LangChain agentic workflows",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your Swift app's needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization of supervisor agent
supervisor = None

def get_supervisor():
    """Get supervisor instance with lazy initialization"""
    global supervisor
    if supervisor is None:
        supervisor = RunningCoachSupervisor()
    return supervisor

# Initialize Supabase Auth
supabase_auth = get_supabase_auth()


# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate authentication token

    Supports two authentication methods:
    1. Supabase JWT tokens (recommended for production)
    2. Simple API key (for backwards compatibility)
    """
    token = credentials.credentials

    # Try Supabase JWT validation first
    if token and token != settings.SWIFT_APP_API_KEY:
        try:
            # Validate JWT token and extract user info
            user_info = supabase_auth.validate_token(token)
            logger.info(f"Authenticated user via JWT: {user_info.get('email')}")
            return user_info
        except HTTPException as e:
            # If JWT validation fails, re-raise the exception
            logger.warning(f"JWT validation failed: {e.detail}")
            raise

    # Fallback to simple API key authentication (backwards compatibility)
    if token == settings.SWIFT_APP_API_KEY:
        logger.info("Authenticated via API key (legacy)")
        return {
            "user_id": "api_key_auth",
            "auth_user_id": None,
            "auth_method": "api_key"
        }

    # No valid authentication
    raise HTTPException(status_code=401, detail="Invalid authentication token")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Runaway Coach API",
        "version": "0.1.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents": {
            "supervisor": "active",
            "performance": "active",
            "goal": "active",
            "workout": "active",
            "pace": "active",
            "weather_context": "active",
            "vo2max_estimation": "active",
            "training_load": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

# Import and include routers
from .routes.analysis import router as analysis_router
from .routes.feedback import router as feedback_router
from .routes.goals import router as goals_router
from .routes.langgraph import router as langgraph_router
from .routes.enhanced_analysis import router as enhanced_analysis_router
from .routes.quick_wins import router as quick_wins_router
from .routes.chat import router as chat_router

app.include_router(analysis_router)
app.include_router(feedback_router)
app.include_router(goals_router)
app.include_router(langgraph_router)
app.include_router(enhanced_analysis_router)
app.include_router(quick_wins_router, prefix="/quick-wins", tags=["Quick Wins"])
app.include_router(chat_router)

# Add startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting Runaway Coach API")
    logger.info(f"Claude Model: {settings.CLAUDE_MODEL}")
    logger.info(f"Supabase URL: {settings.SUPABASE_URL}")
    logger.info("API startup complete - agents will be initialized on first use")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down Runaway Coach API")

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )