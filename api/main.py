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

# Initialize supervisor agent
supervisor = RunningCoachSupervisor()

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate authentication token from Swift app"""
    token = credentials.credentials
    # Implement your authentication logic here
    # This should validate the token from your Swift app
    if not token or token != settings.SWIFT_APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return {"user_id": "authenticated"}

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
            "pace": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

# Import and include routers
from .routes.analysis import router as analysis_router
from .routes.feedback import router as feedback_router  
from .routes.goals import router as goals_router

app.include_router(analysis_router)
app.include_router(feedback_router)
app.include_router(goals_router)

# Add startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting Runaway Coach API")
    logger.info(f"Claude Model: {settings.CLAUDE_MODEL}")
    logger.info(f"Supabase URL: {settings.SUPABASE_URL}")
    
    # Initialize agents
    try:
        if supervisor.client is not None:
            # Test Anthropic API connection
            test_response = await supervisor.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=10,
                messages=[{"role": "user", "content": "Health check"}]
            )
            logger.info("Anthropic API connection successful")
        else:
            logger.info("Anthropic API not available - using fallback mode")
    except Exception as e:
        logger.error(f"Anthropic API connection failed: {str(e)}")

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