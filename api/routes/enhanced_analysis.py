"""
Enhanced Analysis Routes

New API endpoints that use the full Strava data model for comprehensive analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime

from models.strava import Athlete, AthleteStats, EnhancedActivity, RunningGoal
from integrations.supabase_client import SupabaseClient
from integrations.supabase_queries import SupabaseQueries
from core.agents.performance_agent import PerformanceAnalysisAgent
from core.agents.goal_strategy_agent import GoalStrategyAgent
from core.agents.workout_planning_agent import WorkoutPlanningAgent
from core.workflows.enhanced_runner_analysis_workflow import EnhancedRunnerAnalysisWorkflow
from api.main import get_current_user
from utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/enhanced", tags=["enhanced"])

# Initialize clients
supabase_client = SupabaseClient()
supabase_queries = supabase_client.queries


@router.post("/analysis/performance")
async def enhanced_performance_analysis(
    auth_user_id: str,
    limit: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Enhanced performance analysis with weather, HR, elevation, and cadence insights

    Args:
        auth_user_id: Supabase auth user ID
        limit: Number of recent activities to analyze (default: 30)

    Returns:
        Comprehensive performance analysis with AI insights
    """
    start_time = time.time()

    try:
        # Get athlete data
        athlete = await supabase_queries.get_athlete(auth_user_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        # Get athlete stats and activities
        stats = await supabase_queries.get_athlete_stats(athlete.id)
        activities = await supabase_queries.get_recent_activities(athlete.id, limit=limit)

        if not stats:
            raise HTTPException(status_code=404, detail="Athlete stats not found")

        # Run enhanced analysis
        performance_agent = PerformanceAnalysisAgent()
        analysis = await performance_agent.analyze_performance_enhanced(
            athlete=athlete,
            stats=stats,
            activities=activities
        )

        processing_time = time.time() - start_time

        return {
            "success": True,
            "athlete_id": athlete.id,
            "analysis": {
                "metrics": {
                    "weekly_mileage": analysis.metrics.weekly_mileage,
                    "recent_trend": analysis.metrics.recent_trend.value,
                    "consistency": analysis.metrics.consistency,
                    "avg_pace": analysis.metrics.avg_pace
                },
                "strengths": analysis.strengths,
                "recommendations": analysis.recommendations,
                "analysis_date": analysis.analysis_date
            },
            "athlete_stats": {
                "total_activities": stats.count,
                "total_distance_miles": (float(stats.distance) / 1000) * 0.621371,
                "total_moving_time_hours": stats.moving_time / 3600,
                "total_elevation_gain_meters": float(stats.elevation_gain),
                "ytd_distance_miles": (float(stats.ytd_distance) / 1000) * 0.621371,
                "achievements": stats.achievement_count
            },
            "activities_analyzed": len(activities),
            "processing_time": processing_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced performance analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/goals/assess")
async def assess_running_goals(
    auth_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Assess app-specific running goals with auto-progress tracking

    Args:
        auth_user_id: Supabase auth user ID

    Returns:
        Goal assessments with progress, feasibility, and recommendations
    """
    start_time = time.time()

    try:
        # Get athlete
        athlete = await supabase_queries.get_athlete(auth_user_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        # Run enhanced goal assessment
        goal_agent = GoalStrategyAgent(supabase_queries=supabase_queries)
        assessments = await goal_agent.assess_running_goals_enhanced(athlete.id)

        processing_time = time.time() - start_time

        return {
            "success": True,
            "athlete_id": athlete.id,
            "goal_count": len(assessments),
            "assessments": [
                {
                    "goal_id": assessment.goal_id,
                    "goal_type": assessment.goal_type.value,
                    "current_status": assessment.current_status.value,
                    "progress_percentage": assessment.progress_percentage,
                    "feasibility_score": assessment.feasibility_score,
                    "recommendations": assessment.recommendations,
                    "timeline_adjustments": assessment.timeline_adjustments,
                    "key_metrics": assessment.key_metrics
                }
                for assessment in assessments
            ],
            "processing_time": processing_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Goal assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.post("/goals/commitments")
async def track_commitments(
    auth_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Track daily commitments and streak maintenance

    Args:
        auth_user_id: Supabase auth user ID

    Returns:
        Streak information and fulfillment rate
    """
    start_time = time.time()

    try:
        # Get athlete
        athlete = await supabase_queries.get_athlete(auth_user_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        # Track commitments
        goal_agent = GoalStrategyAgent(supabase_queries=supabase_queries)
        tracking = await goal_agent.track_daily_commitments(athlete.id)

        processing_time = time.time() - start_time

        return {
            "success": True,
            "athlete_id": athlete.id,
            "tracking": tracking,
            "processing_time": processing_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Commitment tracking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tracking failed: {str(e)}")


@router.post("/workouts/plan")
async def plan_enhanced_workouts(
    auth_user_id: str,
    goal_id: Optional[int] = None,
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Plan workouts with gear rotation and segment recommendations

    Args:
        auth_user_id: Supabase auth user ID
        goal_id: Optional running goal ID to plan toward
        days: Number of days to plan (default: 7)

    Returns:
        Weekly workout plan with gear and segment recommendations
    """
    start_time = time.time()

    try:
        # Get athlete
        athlete = await supabase_queries.get_athlete(auth_user_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        # Plan workouts
        workout_agent = WorkoutPlanningAgent(supabase_queries=supabase_queries)
        workouts = await workout_agent.plan_workouts_enhanced(
            athlete_id=athlete.id,
            goal_id=goal_id,
            days=days
        )

        processing_time = time.time() - start_time

        return {
            "success": True,
            "athlete_id": athlete.id,
            "goal_id": goal_id,
            "workout_count": len(workouts),
            "workouts": [
                {
                    "run_number": workout.run_number,
                    "workout_type": workout.workout_type.value,
                    "scheduled_date": workout.scheduled_date.isoformat(),
                    "duration_minutes": workout.duration_minutes,
                    "distance_km": workout.distance_km,
                    "distance_miles": workout.distance_km * 0.621371,
                    "target_pace": workout.target_pace,
                    "description": workout.description,
                    "recommended_gear": {
                        "gear_id": workout.recommended_gear_id,
                        "gear_name": workout.recommended_gear_name
                    } if workout.recommended_gear_id else None,
                    "segment": {
                        "segment_id": workout.segment_id,
                        "segment_name": workout.segment_name
                    } if workout.segment_id else None
                }
                for workout in workouts
            ],
            "processing_time": processing_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workout planning failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@router.get("/gear/health")
async def analyze_gear_health(
    auth_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze gear health and recommend replacements

    Args:
        auth_user_id: Supabase auth user ID

    Returns:
        Gear health status with replacement recommendations
    """
    start_time = time.time()

    try:
        # Get athlete
        athlete = await supabase_queries.get_athlete(auth_user_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        # Analyze gear health
        workout_agent = WorkoutPlanningAgent(supabase_queries=supabase_queries)
        health_report = await workout_agent.analyze_gear_health(athlete.id)

        processing_time = time.time() - start_time

        return {
            "success": True,
            "athlete_id": athlete.id,
            "gear_health": health_report,
            "processing_time": processing_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gear health analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/athlete/stats")
async def get_athlete_stats(
    auth_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get athlete profile and lifetime statistics

    Args:
        auth_user_id: Supabase auth user ID

    Returns:
        Athlete profile and aggregated statistics
    """
    try:
        # Get athlete and stats
        athlete = await supabase_queries.get_athlete(auth_user_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        stats = await supabase_queries.get_athlete_stats(athlete.id)

        return {
            "success": True,
            "athlete": {
                "id": athlete.id,
                "auth_user_id": athlete.auth_user_id,
                "first_name": athlete.first_name,
                "last_name": athlete.last_name,
                "email": athlete.email,
                "sex": athlete.sex,
                "weight_kg": float(athlete.weight) if athlete.weight else None,
                "location": {
                    "city": athlete.city,
                    "state": athlete.state,
                    "country": athlete.country
                },
                "created_at": athlete.created_at.isoformat()
            },
            "stats": {
                "total_activities": stats.count,
                "total_distance": {
                    "meters": float(stats.distance),
                    "km": float(stats.distance) / 1000,
                    "miles": (float(stats.distance) / 1000) * 0.621371
                },
                "total_moving_time": {
                    "seconds": stats.moving_time,
                    "hours": stats.moving_time / 3600
                },
                "total_elapsed_time": {
                    "seconds": stats.elapsed_time,
                    "hours": stats.elapsed_time / 3600
                },
                "total_elevation_gain": {
                    "meters": float(stats.elevation_gain),
                    "feet": float(stats.elevation_gain) * 3.28084
                },
                "ytd_distance": {
                    "meters": float(stats.ytd_distance),
                    "km": float(stats.ytd_distance) / 1000,
                    "miles": (float(stats.ytd_distance) / 1000) * 0.621371
                },
                "achievement_count": stats.achievement_count,
                "last_updated": stats.updated_at.isoformat()
            } if stats else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get athlete stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/analysis/comprehensive")
async def comprehensive_analysis(
    auth_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Run comprehensive analysis using enhanced workflow

    This endpoint orchestrates all analyses using the enhanced LangGraph workflow:
    - Performance analysis with weather, HR, elevation
    - Goal assessment with auto-progress tracking
    - Daily commitment streak tracking
    - Workout planning with gear rotation and segments
    - Gear health analysis

    Args:
        auth_user_id: Supabase auth user ID

    Returns:
        Complete analysis report with all insights
    """
    start_time = time.time()

    try:
        # Get athlete
        athlete = await supabase_queries.get_athlete(auth_user_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        # Run enhanced workflow
        workflow = EnhancedRunnerAnalysisWorkflow(supabase_queries=supabase_queries)
        analysis = await workflow.analyze_runner(athlete.id)

        processing_time = time.time() - start_time

        return {
            "success": True,
            "analysis": analysis,
            "processing_time": processing_time,
            "workflow_version": "2.0-enhanced"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Export router
__all__ = ["router"]