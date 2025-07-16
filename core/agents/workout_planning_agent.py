from typing import Dict, Any, List
import logging
import os
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class WorkoutType(Enum):
    EASY_RUN = "easy_run"
    TEMPO_RUN = "tempo_run"
    INTERVAL_TRAINING = "interval_training"
    LONG_RUN = "long_run"
    RECOVERY_RUN = "recovery_run"

@dataclass
class Workout:
    workout_type: WorkoutType
    duration_minutes: int
    distance_km: float
    target_pace: str
    description: str
    scheduled_date: datetime
    run_number: int

@dataclass
class WorkoutInsights:
    performance_rating: float
    effort_level: str
    recommendations: List[str]
    next_workout_suggestions: List[str]

class WorkoutPlanningAgent:
    def __init__(self):
        # Load .env file explicitly
        load_dotenv()
        
        self.client = None
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = AsyncAnthropic(api_key=api_key)
        except Exception as e:
            logger.error(f"Anthropic client initialization failed: {e}")
        logger.info("WorkoutPlanningAgent initialized")
    
    async def plan_workouts(self, activities_data: List[Dict[str, Any]], 
                          goal_data: Dict[str, Any], 
                          workout_count: int = 3) -> List[Workout]:
        """Plan workouts based on activities and goals"""
        try:
            # Mock workout planning
            workouts = [
                Workout(
                    workout_type=WorkoutType.EASY_RUN,
                    duration_minutes=45,
                    distance_km=8.0,
                    target_pace="8:30",
                    description="Easy conversational pace run",
                    scheduled_date=datetime.now(),
                    run_number=1
                ),
                Workout(
                    workout_type=WorkoutType.TEMPO_RUN,
                    duration_minutes=35,
                    distance_km=6.0,
                    target_pace="7:45",
                    description="Tempo run at threshold pace",
                    scheduled_date=datetime.now(),
                    run_number=2
                ),
                Workout(
                    workout_type=WorkoutType.LONG_RUN,
                    duration_minutes=75,
                    distance_km=12.0,
                    target_pace="9:00",
                    description="Long steady run for endurance",
                    scheduled_date=datetime.now(),
                    run_number=3
                )
            ]
            
            logger.info(f"Planned {len(workouts)} workouts")
            return workouts[:workout_count]
            
        except Exception as e:
            logger.error(f"Workout planning failed: {str(e)}")
            raise
    
    async def analyze_completed_workout(self, activity_data: Dict[str, Any], 
                                      planned_workout: Dict[str, Any] = None) -> WorkoutInsights:
        """Analyze a completed workout and provide insights"""
        try:
            insights = WorkoutInsights(
                performance_rating=8.5,
                effort_level="Moderate",
                recommendations=[
                    "Good pacing throughout the run",
                    "Consider increasing distance next time",
                    "Focus on recovery for next 24 hours"
                ],
                next_workout_suggestions=[
                    "Easy recovery run tomorrow",
                    "Tempo run in 2 days",
                    "Consider adding strength training"
                ]
            )
            
            logger.info(f"Workout analysis completed for activity: {activity_data.get('id', 'unknown')}")
            return insights
            
        except Exception as e:
            logger.error(f"Workout analysis failed: {str(e)}")
            raise