from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time
import logging

from models import WorkoutFeedbackResponse, WorkoutData
from ..main import get_current_user

router = APIRouter(prefix="/feedback", tags=["feedback"])
logger = logging.getLogger(__name__)

@router.post("/workout", response_model=WorkoutFeedbackResponse)
async def workout_feedback(
    workout_data: WorkoutData,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate post-workout insights and feedback
    
    This endpoint provides immediate feedback after a completed workout,
    similar to Runna's Workout Insights feature.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating workout feedback for activity: {workout_data.activity.id}")
        
        # Use workout planning agent for post-workout analysis
        from core.agents.workout_planning_agent import WorkoutPlanningAgent
        
        workout_agent = WorkoutPlanningAgent()
        
        insights = await workout_agent.analyze_completed_workout(
            workout_data.activity.dict(),
            workout_data.planned_workout
        )
        
        processing_time = time.time() - start_time
        
        return WorkoutFeedbackResponse(
            success=True,
            insights=insights,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Workout feedback failed: {str(e)}")
        
        return WorkoutFeedbackResponse(
            success=False,
            error_message=str(e),
            processing_time=processing_time
        )

@router.post("/pace-recommendation")
async def pace_recommendation(
    activities_data: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """Generate pace recommendations based on recent performance"""
    try:
        from core.agents.pace_optimization_agent import PaceOptimizationAgent
        
        pace_agent = PaceOptimizationAgent()
        optimization = await pace_agent.optimize_paces(activities_data)
        
        return {
            "success": True,
            "pace_optimization": optimization
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pace recommendation failed: {str(e)}")