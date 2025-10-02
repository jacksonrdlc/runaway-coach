"""
Quick Wins API Routes

New competitive features: Weather Context, VO2 Max Estimation, Training Load Analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
import logging
from datetime import datetime

from integrations.supabase_client import SupabaseClient
from core.agents.weather_context_agent import WeatherContextAgent
from core.agents.vo2max_estimation_agent import VO2MaxEstimationAgent
from core.agents.training_load_agent import TrainingLoadAgent
from utils.auth import get_supabase_auth
from utils.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize settings and auth
settings = get_settings()
supabase_auth = get_supabase_auth()
security = HTTPBearer()

# Initialize agents (will be lazy-loaded on first request)
weather_agent = None
vo2max_agent = None
training_load_agent = None
supabase_client = None


# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate authentication token"""
    token = credentials.credentials

    # Try Supabase JWT validation first
    if token and token != settings.SWIFT_APP_API_KEY:
        try:
            user_info = supabase_auth.validate_token(token)
            logger.info(f"Authenticated user via JWT: {user_info.get('email')}")
            return user_info
        except HTTPException as e:
            logger.warning(f"JWT validation failed: {e.detail}")
            raise

    # Fallback to API key authentication
    if token == settings.SWIFT_APP_API_KEY:
        logger.info("Authenticated via API key")
        return {"user_id": "api_key_user", "email": None}

    raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials"
    )


def get_weather_agent() -> WeatherContextAgent:
    """Lazy initialization of WeatherContextAgent"""
    global weather_agent
    if weather_agent is None:
        weather_agent = WeatherContextAgent()
        logger.info("WeatherContextAgent initialized")
    return weather_agent


def get_vo2max_agent() -> VO2MaxEstimationAgent:
    """Lazy initialization of VO2MaxEstimationAgent"""
    global vo2max_agent
    if vo2max_agent is None:
        vo2max_agent = VO2MaxEstimationAgent()
        logger.info("VO2MaxEstimationAgent initialized")
    return vo2max_agent


def get_training_load_agent() -> TrainingLoadAgent:
    """Lazy initialization of TrainingLoadAgent"""
    global training_load_agent
    if training_load_agent is None:
        training_load_agent = TrainingLoadAgent()
        logger.info("TrainingLoadAgent initialized")
    return training_load_agent


def get_supabase_client() -> SupabaseClient:
    """Lazy initialization of SupabaseClient"""
    global supabase_client
    if supabase_client is None:
        supabase_client = SupabaseClient()
        logger.info("SupabaseClient initialized")
    return supabase_client


@router.get("/weather-impact")
async def get_weather_impact(
    user_id: str = None,
    limit: int = 30,
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze weather impact on running performance

    Returns:
    - Average training conditions
    - Heat stress assessment
    - Pace degradation estimates
    - Optimal training times
    - Heat acclimation level
    """
    try:
        agent = get_weather_agent()
        db_client = get_supabase_client()

        # Resolve user_id to athlete_id
        if not user_id:
            # Get auth user ID from JWT token
            auth_user_id = current_user.get("sub") or current_user.get("user_id")
            if not auth_user_id:
                raise HTTPException(status_code=401, detail="No user identifier in token")

            # Look up athlete record to get athlete_id
            athlete = await db_client.queries.get_athlete(auth_user_id)
            if not athlete:
                raise HTTPException(status_code=404, detail="Athlete not found for authenticated user")

            athlete_id = athlete.id
        else:
            # user_id provided as parameter - could be athlete_id or auth_user_id
            # Try as athlete_id first (integer)
            try:
                athlete_id = int(user_id)
            except ValueError:
                # Not an integer, must be auth_user_id (UUID)
                athlete = await db_client.queries.get_athlete(user_id)
                if not athlete:
                    raise HTTPException(status_code=404, detail="Athlete not found")
                athlete_id = athlete.id

        # Fetch activities
        activities = await db_client.queries.get_recent_activities(
            athlete_id=athlete_id,
            limit=limit
        )

        if not activities:
            raise HTTPException(status_code=404, detail="No activities found for user")

        # Convert to dict format
        activities_data = [
            {
                "activity_date": activity.activity_date,
                "start_latitude": activity.start_latitude,
                "start_longitude": activity.start_longitude,
                "distance": activity.distance,
                "elapsed_time": activity.elapsed_time,
                "average_temperature": activity.average_temperature,
                "humidity": activity.humidity
            }
            for activity in activities
        ]

        # Analyze weather impact
        analysis = await agent.analyze_weather_impact(activities_data)

        return {
            "success": True,
            "analysis": {
                "average_temperature_celsius": analysis.average_temperature,
                "average_humidity_percent": analysis.average_humidity,
                "heat_stress_runs": analysis.heat_stress_runs,
                "ideal_condition_runs": analysis.ideal_condition_runs,
                "weather_impact_score": analysis.weather_impact_score.value,
                "pace_degradation_seconds_per_mile": analysis.pace_degradation_estimate,
                "heat_acclimation_level": analysis.heat_acclimation_level,
                "optimal_training_times": analysis.optimal_training_times,
                "recommendations": analysis.recommendations,
                "analysis_period": analysis.analysis_period
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weather impact analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/vo2max-estimate")
async def get_vo2max_estimate(
    user_id: str = None,
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """
    Estimate VO2 max and predict race times

    Returns:
    - VO2 max estimate (ml/kg/min)
    - Fitness level category
    - Race time predictions (5K, 10K, Half, Full Marathon)
    - vVO2 max pace
    - Training recommendations
    """
    try:
        agent = get_vo2max_agent()
        db_client = get_supabase_client()

        # Resolve user_id to athlete_id
        if not user_id:
            # Get auth user ID from JWT token
            auth_user_id = current_user.get("sub") or current_user.get("user_id")
            if not auth_user_id:
                raise HTTPException(status_code=401, detail="No user identifier in token")

            # Look up athlete record to get athlete_id
            athlete = await db_client.queries.get_athlete(auth_user_id)
            if not athlete:
                raise HTTPException(status_code=404, detail="Athlete not found for authenticated user")

            athlete_id = athlete.id
        else:
            # user_id provided as parameter - could be athlete_id or auth_user_id
            # Try as athlete_id first (integer)
            try:
                athlete_id = int(user_id)
            except ValueError:
                # Not an integer, must be auth_user_id (UUID)
                athlete = await db_client.queries.get_athlete(user_id)
                if not athlete:
                    raise HTTPException(status_code=404, detail="Athlete not found")
                athlete_id = athlete.id

        # Fetch activities
        activities = await db_client.queries.get_recent_activities(
            athlete_id=athlete_id,
            limit=limit
        )

        if not activities:
            raise HTTPException(status_code=404, detail="No activities found for user")

        # Convert to dict format
        activities_data = [
            {
                "distance": activity.distance,
                "elapsed_time": activity.elapsed_time,
                "average_speed": activity.average_speed,
                "average_heart_rate": activity.average_heart_rate,
                "max_heart_rate": activity.max_heart_rate,
                "average_watts": activity.average_watts,
                "activity_date": activity.activity_date
            }
            for activity in activities
        ]

        # Estimate VO2 max
        estimate = await agent.estimate_vo2_max(activities_data)

        return {
            "success": True,
            "estimate": {
                "vo2_max": estimate.vo2_max,
                "fitness_level": estimate.current_fitness_level,
                "estimation_method": estimate.estimation_method,
                "vvo2_max_pace": estimate.vvo2_max_pace,
                "race_predictions": [
                    {
                        "distance": pred.distance_name,
                        "distance_km": pred.distance_km,
                        "predicted_time": f"{pred.predicted_time_seconds // 3600}:{(pred.predicted_time_seconds % 3600) // 60:02d}:{pred.predicted_time_seconds % 60:02d}",
                        "predicted_time_seconds": pred.predicted_time_seconds,
                        "pace_per_km": pred.predicted_pace_per_km,
                        "pace_per_mile": pred.predicted_pace_per_mile,
                        "confidence": pred.confidence_level
                    }
                    for pred in estimate.race_predictions
                ],
                "recommendations": estimate.recommendations,
                "data_quality_score": estimate.data_quality_score
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"VO2 max estimation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")


@router.get("/training-load")
async def get_training_load(
    user_id: str = None,
    limit: int = 60,
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze training load and recovery status

    Returns:
    - Acute:Chronic Workload Ratio (ACWR)
    - Training Stress Score (TSS)
    - Recovery status
    - Injury risk level
    - Daily workout recommendations (next 7 days)
    """
    try:
        agent = get_training_load_agent()
        db_client = get_supabase_client()

        # Resolve user_id to athlete_id
        if not user_id:
            # Get auth user ID from JWT token
            auth_user_id = current_user.get("sub") or current_user.get("user_id")
            if not auth_user_id:
                raise HTTPException(status_code=401, detail="No user identifier in token")

            # Look up athlete record to get athlete_id
            athlete = await db_client.queries.get_athlete(auth_user_id)
            if not athlete:
                raise HTTPException(status_code=404, detail="Athlete not found for authenticated user")

            athlete_id = athlete.id
        else:
            # user_id provided as parameter - could be athlete_id or auth_user_id
            # Try as athlete_id first (integer)
            try:
                athlete_id = int(user_id)
            except ValueError:
                # Not an integer, must be auth_user_id (UUID)
                athlete = await db_client.queries.get_athlete(user_id)
                if not athlete:
                    raise HTTPException(status_code=404, detail="Athlete not found")
                athlete_id = athlete.id

        # Fetch activities (need at least 28 days for chronic load)
        activities = await db_client.queries.get_recent_activities(
            athlete_id=athlete_id,
            limit=limit
        )

        if not activities:
            raise HTTPException(status_code=404, detail="No activities found for user")

        # Convert to dict format
        activities_data = [
            {
                "activity_date": activity.activity_date,
                "distance": activity.distance,
                "elapsed_time": activity.elapsed_time,
                "average_heart_rate": activity.average_heart_rate,
                "max_heart_rate": activity.max_heart_rate,
                "average_speed": activity.average_speed
            }
            for activity in activities
        ]

        # Analyze training load
        analysis = await agent.analyze_training_load(activities_data)

        return {
            "success": True,
            "analysis": {
                "acute_load_7_days": analysis.acute_load,
                "chronic_load_28_days": analysis.chronic_load,
                "acwr": analysis.acwr,
                "weekly_tss": analysis.weekly_tss,
                "total_volume_km": analysis.total_volume_km,
                "recovery_status": analysis.recovery_status.value,
                "injury_risk_level": analysis.injury_risk_level,
                "training_trend": analysis.training_trend.value,
                "fitness_trend": analysis.fitness_trend,
                "recommendations": analysis.recommendations,
                "daily_recommendations": analysis.daily_recommendations
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training load analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/comprehensive-analysis")
async def get_comprehensive_analysis(
    user_id: str = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all quick win analyses in a single response

    Returns combined analysis from:
    - Weather Context
    - VO2 Max Estimation
    - Training Load
    """
    try:
        # Resolve user_id to athlete_id
        db_client = get_supabase_client()

        if not user_id:
            # Get auth user ID from JWT token
            auth_user_id = current_user.get("sub") or current_user.get("user_id")
            if not auth_user_id:
                raise HTTPException(status_code=401, detail="No user identifier in token")

            # Look up athlete record to get athlete_id
            athlete = await db_client.queries.get_athlete(auth_user_id)
            if not athlete:
                raise HTTPException(status_code=404, detail="Athlete not found for authenticated user")

            resolved_user_id = str(athlete.id)
        else:
            # user_id provided as parameter - could be athlete_id or auth_user_id
            # Try as athlete_id first (integer)
            try:
                int(user_id)  # Test if it's an integer
                resolved_user_id = user_id
            except ValueError:
                # Not an integer, must be auth_user_id (UUID)
                athlete = await db_client.queries.get_athlete(user_id)
                if not athlete:
                    raise HTTPException(status_code=404, detail="Athlete not found")
                resolved_user_id = str(athlete.id)

        # Run all analyses in parallel
        import asyncio

        weather_task = get_weather_impact(user_id=resolved_user_id, current_user=current_user)
        vo2max_task = get_vo2max_estimate(user_id=resolved_user_id, current_user=current_user)
        training_load_task = get_training_load(user_id=resolved_user_id, current_user=current_user)

        weather_result, vo2max_result, training_load_result = await asyncio.gather(
            weather_task,
            vo2max_task,
            training_load_task,
            return_exceptions=True
        )

        # Build comprehensive response
        response = {
            "success": True,
            "athlete_id": resolved_user_id,
            "analysis_date": datetime.now().isoformat(),
            "analyses": {}
        }

        # Add successful analyses
        if not isinstance(weather_result, Exception):
            response["analyses"]["weather_context"] = weather_result.get("analysis", {})
        else:
            logger.warning(f"Weather analysis failed: {weather_result}")

        if not isinstance(vo2max_result, Exception):
            response["analyses"]["vo2max_estimate"] = vo2max_result.get("estimate", {})
        else:
            logger.warning(f"VO2 max estimation failed: {vo2max_result}")

        if not isinstance(training_load_result, Exception):
            response["analyses"]["training_load"] = training_load_result.get("analysis", {})
        else:
            logger.warning(f"Training load analysis failed: {training_load_result}")

        # Generate priority recommendations
        all_recommendations = []
        if "training_load" in response["analyses"]:
            all_recommendations.extend(
                response["analyses"]["training_load"].get("recommendations", [])[:2]
            )
        if "vo2max_estimate" in response["analyses"]:
            all_recommendations.extend(
                response["analyses"]["vo2max_estimate"].get("recommendations", [])[:1]
            )
        if "weather_context" in response["analyses"]:
            all_recommendations.extend(
                response["analyses"]["weather_context"].get("recommendations", [])[:1]
            )

        response["priority_recommendations"] = all_recommendations[:5]

        return response

    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
