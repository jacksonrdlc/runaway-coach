from typing import Dict, Any, List, Optional
import logging
import os
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from dotenv import load_dotenv

from models.strava import EnhancedActivity, Gear, Segment, RunningGoal
from integrations.supabase_queries import SupabaseQueries

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
    recommended_gear_id: Optional[int] = None
    recommended_gear_name: Optional[str] = None
    segment_id: Optional[int] = None
    segment_name: Optional[str] = None

@dataclass
class WorkoutInsights:
    performance_rating: float
    effort_level: str
    recommendations: List[str]
    next_workout_suggestions: List[str]

class WorkoutPlanningAgent:
    def __init__(self, supabase_queries: Optional[SupabaseQueries] = None):
        # Load .env file explicitly
        load_dotenv()

        self.client = None
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = AsyncAnthropic(api_key=api_key)
        except Exception as e:
            logger.error(f"Anthropic client initialization failed: {e}")

        self.supabase = supabase_queries
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

    # =====================================
    # Enhanced Workout Planning Methods
    # =====================================

    async def plan_workouts_enhanced(
        self,
        athlete_id: int,
        goal_id: Optional[int] = None,
        days: int = 7
    ) -> List[Workout]:
        """Plan workouts with gear rotation and segment recommendations"""
        if not self.supabase:
            logger.error("Supabase queries not initialized")
            return []

        try:
            # Get athlete's data
            gear_list = await self.supabase.get_athlete_gear(athlete_id, gear_type="shoes")
            activities = await self.supabase.get_recent_activities(athlete_id, limit=20)
            starred_segments = await self.supabase.get_starred_segments(athlete_id)

            goal = None
            if goal_id:
                goal = await self.supabase.get_running_goal(goal_id)

            workouts = []
            for day in range(days):
                # Rotate gear to distribute mileage
                recommended_gear = self._recommend_gear_rotation(gear_list, activities, day)

                # Select segment for tempo/interval workouts
                segment = self._select_segment_for_day(starred_segments, day)

                # Generate workout
                workout = await self._generate_enhanced_workout(
                    day=day,
                    goal=goal,
                    gear=recommended_gear,
                    segment=segment,
                    activities=activities
                )
                workouts.append(workout)

            logger.info(f"Planned {len(workouts)} enhanced workouts for athlete {athlete_id}")
            return workouts

        except Exception as e:
            logger.error(f"Enhanced workout planning failed: {str(e)}")
            return []

    def _recommend_gear_rotation(
        self,
        gear_list: List[Gear],
        activities: List[EnhancedActivity],
        day: int
    ) -> Optional[Gear]:
        """Recommend gear rotation based on mileage and usage patterns"""
        if not gear_list:
            return None

        # Calculate recent usage for each gear
        gear_usage = {}
        for gear in gear_list:
            recent_miles = sum(
                (float(a.distance) / 1000) * 0.621371
                for a in activities[-10:]
                if a.gear_id == gear.id
            )
            gear_usage[gear.id] = recent_miles

            # Warn if gear needs replacement (>400 miles for shoes)
            total_miles = (gear.total_distance / 1000) * 0.621371
            if total_miles > 400 and gear.gear_type == "shoes":
                logger.warning(
                    f"Gear '{gear.name}' has {total_miles:.0f} miles - consider replacing soon"
                )

        # Return gear with lowest recent usage to distribute wear evenly
        least_used_gear = min(gear_list, key=lambda g: gear_usage.get(g.id, 0))
        return least_used_gear

    def _select_segment_for_day(
        self,
        segments: List[Segment],
        day: int
    ) -> Optional[Segment]:
        """Select a segment for workout variety"""
        if not segments:
            return None

        # Rotate through segments
        segment_index = day % len(segments)
        return segments[segment_index]

    async def _generate_enhanced_workout(
        self,
        day: int,
        goal: Optional[RunningGoal],
        gear: Optional[Gear],
        segment: Optional[Segment],
        activities: List[EnhancedActivity]
    ) -> Workout:
        """Generate a single workout with gear and segment recommendations"""

        # Determine workout type based on day of week
        workout_types_cycle = [
            WorkoutType.EASY_RUN,
            WorkoutType.TEMPO_RUN,
            WorkoutType.EASY_RUN,
            WorkoutType.INTERVAL_TRAINING,
            WorkoutType.EASY_RUN,
            WorkoutType.LONG_RUN,
            WorkoutType.RECOVERY_RUN,
        ]
        workout_type = workout_types_cycle[day % 7]

        # Calculate target pace based on recent performance
        target_pace = self._calculate_target_pace(activities, workout_type)

        # Set duration and distance
        if workout_type == WorkoutType.LONG_RUN:
            duration_minutes = 90
            distance_km = 15.0
        elif workout_type == WorkoutType.TEMPO_RUN:
            duration_minutes = 45
            distance_km = 8.0
        elif workout_type == WorkoutType.INTERVAL_TRAINING:
            duration_minutes = 40
            distance_km = 7.0
        elif workout_type == WorkoutType.RECOVERY_RUN:
            duration_minutes = 30
            distance_km = 5.0
        else:  # EASY_RUN
            duration_minutes = 45
            distance_km = 8.0

        # Build description
        description = self._build_workout_description(
            workout_type, gear, segment, goal
        )

        scheduled_date = datetime.now() + timedelta(days=day)

        return Workout(
            workout_type=workout_type,
            duration_minutes=duration_minutes,
            distance_km=distance_km,
            target_pace=target_pace,
            description=description,
            scheduled_date=scheduled_date,
            run_number=day + 1,
            recommended_gear_id=gear.id if gear else None,
            recommended_gear_name=gear.name if gear else None,
            segment_id=segment.id if segment else None,
            segment_name=segment.name if segment else None
        )

    def _calculate_target_pace(
        self,
        activities: List[EnhancedActivity],
        workout_type: WorkoutType
    ) -> str:
        """Calculate target pace based on recent performance"""
        if not activities:
            # Default paces
            pace_map = {
                WorkoutType.EASY_RUN: "9:00",
                WorkoutType.RECOVERY_RUN: "9:30",
                WorkoutType.LONG_RUN: "9:15",
                WorkoutType.TEMPO_RUN: "7:45",
                WorkoutType.INTERVAL_TRAINING: "7:00",
            }
            return pace_map.get(workout_type, "8:30")

        # Calculate average pace from recent runs
        recent_paces = []
        for a in activities[:5]:
            if a.distance and a.moving_time:
                miles = (float(a.distance) / 1000) * 0.621371
                pace = a.moving_time / 60 / miles if miles > 0 else 0
                if pace > 0:
                    recent_paces.append(pace)

        if not recent_paces:
            return "8:30"

        avg_pace = sum(recent_paces) / len(recent_paces)

        # Adjust based on workout type
        if workout_type == WorkoutType.EASY_RUN:
            target_pace = avg_pace * 1.15  # 15% slower
        elif workout_type == WorkoutType.RECOVERY_RUN:
            target_pace = avg_pace * 1.20  # 20% slower
        elif workout_type == WorkoutType.LONG_RUN:
            target_pace = avg_pace * 1.10  # 10% slower
        elif workout_type == WorkoutType.TEMPO_RUN:
            target_pace = avg_pace * 0.95  # 5% faster
        elif workout_type == WorkoutType.INTERVAL_TRAINING:
            target_pace = avg_pace * 0.90  # 10% faster
        else:
            target_pace = avg_pace

        # Format as MM:SS
        minutes = int(target_pace)
        seconds = int((target_pace % 1) * 60)
        return f"{minutes}:{seconds:02d}"

    def _build_workout_description(
        self,
        workout_type: WorkoutType,
        gear: Optional[Gear],
        segment: Optional[Segment],
        goal: Optional[RunningGoal]
    ) -> str:
        """Build descriptive workout text"""
        descriptions = {
            WorkoutType.EASY_RUN: "Easy conversational pace run",
            WorkoutType.RECOVERY_RUN: "Recovery run at very easy pace",
            WorkoutType.LONG_RUN: "Long steady run for endurance building",
            WorkoutType.TEMPO_RUN: "Tempo run at comfortably hard pace",
            WorkoutType.INTERVAL_TRAINING: "Interval training for speed development",
        }

        base_description = descriptions.get(workout_type, "Training run")

        # Add gear recommendation
        if gear:
            total_miles = (gear.total_distance / 1000) * 0.621371
            base_description += f" | Recommended shoes: {gear.name} ({total_miles:.0f} miles)"

        # Add segment challenge
        if segment and workout_type in [WorkoutType.TEMPO_RUN, WorkoutType.INTERVAL_TRAINING]:
            base_description += f" | Try for PR on '{segment.name}' segment"

        # Add goal context
        if goal:
            base_description += f" | Working toward: {goal.title}"

        return base_description

    async def analyze_gear_health(self, athlete_id: int) -> Dict[str, Any]:
        """Analyze gear health and recommend replacements"""
        if not self.supabase:
            logger.error("Supabase queries not initialized")
            return {}

        try:
            gear_list = await self.supabase.get_athlete_gear(athlete_id)

            gear_health = []
            for gear in gear_list:
                total_miles = (gear.total_distance / 1000) * 0.621371

                # Assess health
                if gear.gear_type == "shoes":
                    if total_miles > 500:
                        status = "replace_now"
                        recommendation = f"Replace immediately - {total_miles:.0f} miles exceeds safe limit"
                    elif total_miles > 400:
                        status = "replace_soon"
                        recommendation = f"Consider replacing soon - {total_miles:.0f} miles"
                    elif total_miles > 300:
                        status = "monitor"
                        recommendation = f"Monitor closely - {total_miles:.0f} miles"
                    else:
                        status = "healthy"
                        recommendation = f"Good condition - {total_miles:.0f} miles"
                else:
                    status = "healthy"
                    recommendation = f"Bike gear - {total_miles:.0f} miles"

                gear_health.append({
                    "gear_id": gear.id,
                    "gear_name": gear.name,
                    "gear_type": gear.gear_type,
                    "total_miles": total_miles,
                    "status": status,
                    "recommendation": recommendation,
                    "is_primary": gear.is_primary
                })

            return {
                "gear_count": len(gear_list),
                "gear_health": gear_health,
                "needs_replacement": [g for g in gear_health if g["status"] == "replace_now"],
                "needs_attention": [g for g in gear_health if g["status"] == "replace_soon"]
            }

        except Exception as e:
            logger.error(f"Gear health analysis failed: {str(e)}")
            return {}