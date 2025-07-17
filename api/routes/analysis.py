from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List
import time
import logging

from models import AnalysisResponse
from core.agents.supervisor_agent import RunningCoachSupervisor

router = APIRouter(prefix="/analysis", tags=["analysis"])
logger = logging.getLogger(__name__)

# Import get_current_user from main module
from ..main import get_current_user

# Import lazy supervisor getter
from ..main import get_supervisor

@router.post("/runner", response_model=AnalysisResponse)
async def analyze_runner(
    runner_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Comprehensive runner analysis using agentic workflow
    
    Expected runner_data format:
    {
        "user_id": int,
        "activities": [Activity objects],
        "goals": [Goal objects],
        "profile": RunnerProfile object,
        "preferences": Optional[RunnerPreferences]
    }
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting analysis for user: {runner_data.get('user_id', 'unknown')}")
        
        # Validate input data
        if not runner_data.get("activities"):
            raise HTTPException(status_code=400, detail="Activities data is required")
        
        # Run comprehensive analysis using lazy-initialized supervisor
        supervisor = get_supervisor()
        analysis = await supervisor.analyze_runner(runner_data)
        
        processing_time = time.time() - start_time
        logger.info(f"Analysis completed in {processing_time:.2f} seconds")
        
        # Schedule background tasks for data persistence, notifications, etc.
        background_tasks.add_task(
            log_analysis_completion,
            runner_data.get("user_id"),
            processing_time,
            analysis.agent_metadata
        )
        
        return AnalysisResponse(
            success=True,
            analysis=analysis,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Analysis failed: {str(e)}")
        
        return AnalysisResponse(
            success=False,
            error_message=str(e),
            processing_time=processing_time
        )

@router.post("/quick-insights")
async def quick_performance_insights(
    activities_data: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """Quick performance insights without full analysis"""
    try:
        # Use just the performance agent for quick insights
        from core.agents.performance_agent import PerformanceAnalysisAgent
        
        performance_agent = PerformanceAnalysisAgent()
        analysis = await performance_agent.analyze_performance(activities_data)
        
        return {
            "success": True,
            "insights": {
                "performance_trend": analysis.metrics.recent_trend.value,
                "weekly_mileage": analysis.metrics.weekly_mileage,
                "consistency": analysis.metrics.consistency,
                "key_strengths": analysis.strengths[:3],
                "top_recommendations": analysis.recommendations[:3]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick insights failed: {str(e)}")

async def log_analysis_completion(user_id: int, processing_time: float, metadata: Dict):
    """Background task for logging analysis completion"""
    logger.info(f"Analysis completed for user {user_id} in {processing_time:.2f}s")
    # Could log to database, send notifications, etc.