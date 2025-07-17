from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import asdict
import logging

from ..main import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])
logger = logging.getLogger(__name__)

@router.post("/assess")
async def assess_goals(
    goals_data: List[Dict[str, Any]],
    activities_data: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """Assess goal feasibility and progress"""
    try:
        from core.agents.goal_strategy_agent import GoalStrategyAgent
        
        goal_agent = GoalStrategyAgent()
        assessments = await goal_agent.assess_goals(goals_data, activities_data)
        
        return {
            "success": True,
            "goal_assessments": [asdict(assessment) for assessment in assessments]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Goal assessment failed: {str(e)}")

@router.post("/training-plan")
async def generate_training_plan(
    goal_data: Dict[str, Any],
    activities_data: List[Dict[str, Any]],
    plan_duration_weeks: int = 12,
    current_user: dict = Depends(get_current_user)
):
    """Generate a training plan for a specific goal"""
    try:
        from core.agents.workout_planning_agent import WorkoutPlanningAgent
        
        workout_agent = WorkoutPlanningAgent()
        
        # Generate workouts for the specified duration
        weekly_workouts = []
        for week in range(plan_duration_weeks):
            week_workouts = await workout_agent.plan_workouts(
                activities_data, 
                goal_data, 
                workout_count=3  # 3 workouts per week
            )
            
            # Adjust workouts for progression over time
            for workout in week_workouts:
                workout.scheduled_date = datetime.now() + timedelta(weeks=week, days=workout.run_number*2)
                
            weekly_workouts.append({
                "week": week + 1,
                "workouts": [asdict(w) for w in week_workouts]
            })
        
        return {
            "success": True,
            "training_plan": {
                "goal": goal_data,
                "duration_weeks": plan_duration_weeks,
                "weekly_schedule": weekly_workouts
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training plan generation failed: {str(e)}")