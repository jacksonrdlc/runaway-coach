from typing import Dict, Any, List, Optional
import logging
import os
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from dotenv import load_dotenv
from decimal import Decimal

from models.strava import RunningGoal, StravaGoal, EnhancedActivity, DailyCommitment
from integrations.supabase_queries import SupabaseQueries

logger = logging.getLogger(__name__)

class GoalType(Enum):
    RACE_TIME = "race_time"
    DISTANCE = "distance"
    CONSISTENCY = "consistency"
    WEIGHT_LOSS = "weight_loss"
    GENERAL_FITNESS = "general_fitness"

class GoalStatus(Enum):
    ON_TRACK = "on_track"
    BEHIND = "behind"
    AHEAD = "ahead"
    NEEDS_ADJUSTMENT = "needs_adjustment"

@dataclass
class GoalAssessment:
    goal_id: str
    goal_type: GoalType
    current_status: GoalStatus
    progress_percentage: float
    feasibility_score: float
    recommendations: List[str]
    timeline_adjustments: List[str]
    key_metrics: Dict[str, Any]

class GoalStrategyAgent:
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
        logger.info("GoalStrategyAgent initialized")
    
    async def assess_goals(self, goals_data: List[Dict[str, Any]], 
                          activities_data: List[Dict[str, Any]]) -> List[GoalAssessment]:
        """Assess goal feasibility and progress"""
        try:
            assessments = []
            
            for i, goal in enumerate(goals_data):
                # Generate AI-powered goal assessment
                if self.client:
                    assessment = await self._generate_ai_goal_assessment(goal, activities_data)
                else:
                    logger.warning("Anthropic client not available, using fallback goal assessment")
                    assessment = self._get_fallback_goal_assessment(goal, i)
                
                assessments.append(assessment)
            
            logger.info(f"Goal assessment completed for {len(goals_data)} goals")
            return assessments
            
        except Exception as e:
            logger.error(f"Goal assessment failed: {str(e)}")
            raise
    
    async def _generate_ai_goal_assessment(self, goal: Dict[str, Any], activities_data: List[Dict[str, Any]]) -> GoalAssessment:
        """Generate AI-powered goal assessment"""
        try:
            # Prepare context for AI
            goal_context = self._prepare_goal_context(goal, activities_data)
            
            prompt = f"""
            As an expert running coach, assess this runner's goal and provide personalized feedback:

            {goal_context}

            Please provide a JSON response with:
            1. "progress_percentage": Number between 0-100 indicating current progress
            2. "feasibility_score": Number between 0-1 indicating how realistic the goal is
            3. "current_status": One of "ON_TRACK", "BEHIND", "AHEAD", "NEEDS_ADJUSTMENT"
            4. "recommendations": List of 3-5 specific, actionable recommendations
            5. "timeline_adjustments": List of 2-3 timeline-related insights
            6. "key_insights": 2-3 key insights about their progress

            Focus on:
            - Realistic assessment based on current performance
            - Specific, actionable advice
            - Addressing any gaps between current and target performance
            - Timeline feasibility
            - Use MILES for all distance measurements (not kilometers)
            - Provide specific, measurable recommendations

            Respond in JSON format only.
            """
            
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse AI response
            import json
            ai_content = response.content[0].text
            
            try:
                start = ai_content.find('{')
                end = ai_content.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = ai_content[start:end]
                    ai_data = json.loads(json_str)
                    
                    return GoalAssessment(
                        goal_id=goal.get("id", "unknown"),
                        goal_type=self._determine_goal_type(goal),
                        current_status=self._parse_goal_status(ai_data.get("current_status", "ON_TRACK")),
                        progress_percentage=float(ai_data.get("progress_percentage", 50)),
                        feasibility_score=float(ai_data.get("feasibility_score", 0.7)),
                        recommendations=ai_data.get("recommendations", []),
                        timeline_adjustments=ai_data.get("timeline_adjustments", []),
                        key_metrics=self._extract_key_metrics(goal, activities_data)
                    )
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")
                return self._get_fallback_goal_assessment(goal, 0)
                
        except Exception as e:
            logger.error(f"AI goal assessment failed: {str(e)}")
            return self._get_fallback_goal_assessment(goal, 0)
    
    def _prepare_goal_context(self, goal: Dict[str, Any], activities_data: List[Dict[str, Any]]) -> str:
        """Prepare goal context for AI analysis"""
        goal_type = goal.get("type", "unknown")
        target_value = goal.get("target_value", "unknown")
        deadline = goal.get("deadline", "unknown")
        
        # Calculate current performance metrics
        if activities_data:
            recent_distances = [(act.get("distance", 0) / 1000) * 0.621371 for act in activities_data[:5]]  # Convert to miles
            recent_times = [act.get("elapsed_time", 0) for act in activities_data[:5]]
            avg_distance = sum(recent_distances) / len(recent_distances) if recent_distances else 0
            avg_time = sum(recent_times) / len(recent_times) if recent_times else 0
            
            performance_context = f"""
            CURRENT PERFORMANCE:
            - Recent average distance: {avg_distance:.1f} miles
            - Recent average time: {avg_time/60:.1f} minutes
            - Total recent activities: {len(activities_data)}
            - Recent activities: {', '.join([f"{d:.1f} miles" for d in recent_distances[:3]])}
            """
        else:
            performance_context = "No recent activity data available"
        
        return f"""
        GOAL DETAILS:
        - Type: {goal_type}
        - Target: {target_value}
        - Deadline: {deadline}
        - Goal ID: {goal.get("id", "unknown")}
        
        {performance_context}
        """
    
    def _determine_goal_type(self, goal: Dict[str, Any]) -> GoalType:
        """Determine goal type from goal data"""
        goal_type = goal.get("type", "").lower()
        if "race" in goal_type or "time" in goal_type:
            return GoalType.RACE_TIME
        elif "distance" in goal_type:
            return GoalType.DISTANCE
        elif "consistency" in goal_type:
            return GoalType.CONSISTENCY
        elif "weight" in goal_type:
            return GoalType.WEIGHT_LOSS
        else:
            return GoalType.GENERAL_FITNESS
    
    def _parse_goal_status(self, status_str: str) -> GoalStatus:
        """Parse goal status from AI response"""
        status_str = status_str.upper()
        if "BEHIND" in status_str:
            return GoalStatus.BEHIND
        elif "AHEAD" in status_str:
            return GoalStatus.AHEAD
        elif "NEEDS_ADJUSTMENT" in status_str:
            return GoalStatus.NEEDS_ADJUSTMENT
        else:
            return GoalStatus.ON_TRACK
    
    def _extract_key_metrics(self, goal: Dict[str, Any], activities_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key metrics for goal assessment"""
        # Calculate current pace from recent activities
        current_pace = "8:15"  # Default fallback
        target_pace = "7:45"   # Default target
        weekly_mileage = 15.5  # Default weekly mileage (~25km in miles)
        target_mileage = 21.7  # Default target mileage (~35km in miles)
        
        if activities_data:
            # Calculate average pace from recent activities
            total_distance = sum(act.get("distance", 0) for act in activities_data[:5])
            total_time = sum(act.get("elapsed_time", 0) for act in activities_data[:5])
            
            if total_distance > 0 and total_time > 0:
                avg_pace_seconds = total_time / (total_distance / 1000)  # seconds per km
                pace_minutes = int(avg_pace_seconds // 60)
                pace_seconds = int(avg_pace_seconds % 60)
                current_pace = f"{pace_minutes}:{pace_seconds:02d}"
            
            # Calculate weekly mileage
            weekly_mileage = (total_distance / 1000) * 0.621371  # Convert to miles
            
            # Estimate target based on goal type
            if "race" in goal.get("type", "").lower():
                target_pace = f"{max(4, pace_minutes-1)}:{pace_seconds:02d}"
            
            target_mileage = weekly_mileage * 1.4  # 40% increase as target
        
        # Return schema that matches iOS expectations
        return {
            "current_pace": current_pace,
            "target_pace": target_pace,
            "weekly_mileage": weekly_mileage,
            "target_mileage": target_mileage,
            "goal_type": goal.get("type", "unknown"),
            "target_value": goal.get("target_value", "unknown"),
            "deadline": goal.get("deadline", "unknown"),
            "weeks_remaining": 12  # Default, could be calculated from deadline
        }
    
    def _get_fallback_goal_assessment(self, goal: Dict[str, Any], index: int) -> GoalAssessment:
        """Fallback goal assessment when AI is not available"""
        return GoalAssessment(
            goal_id=goal.get("id", f"goal_{index}"),
            goal_type=self._determine_goal_type(goal),
            current_status=GoalStatus.ON_TRACK,
            progress_percentage=65.0,
            feasibility_score=0.8,
            recommendations=[
                "Continue current training consistency",
                "Gradually increase training intensity",
                "Monitor progress weekly"
            ],
            timeline_adjustments=[
                "Goal appears achievable in current timeline",
                "Consider regular progress reviews"
            ],
            key_metrics=self._extract_key_metrics(goal, [])
        )
    
    async def create_goal_strategy(self, goal_data: Dict[str, Any],
                                 current_fitness: Dict[str, Any]) -> Dict[str, Any]:
        """Create a strategic plan for achieving a specific goal"""
        try:
            strategy = {
                "goal_breakdown": {
                    "short_term": ["Build base mileage", "Improve running form"],
                    "medium_term": ["Add speed work", "Increase long run distance"],
                    "long_term": ["Peak training", "Taper and race preparation"]
                },
                "weekly_training_structure": {
                    "easy_runs": 3,
                    "tempo_runs": 1,
                    "interval_sessions": 1,
                    "long_runs": 1,
                    "rest_days": 1
                },
                "progression_timeline": {
                    "weeks_1_4": "Base building phase",
                    "weeks_5_8": "Speed development",
                    "weeks_9_12": "Peak training",
                    "weeks_13_16": "Race preparation"
                },
                "success_metrics": [
                    "Weekly mileage progression",
                    "Pace improvements",
                    "Consistency tracking",
                    "Recovery monitoring"
                ]
            }

            logger.info(f"Goal strategy created for goal: {goal_data.get('id', 'unknown')}")
            return strategy

        except Exception as e:
            logger.error(f"Goal strategy creation failed: {str(e)}")
            raise

    # =====================================
    # Enhanced Goal Management Methods
    # =====================================

    async def assess_running_goals_enhanced(
        self,
        athlete_id: int
    ) -> List[GoalAssessment]:
        """Assess app-specific running goals with database integration"""
        if not self.supabase:
            logger.error("Supabase queries not initialized")
            return []

        try:
            # Get running goals and recent activities
            running_goals = await self.supabase.get_running_goals(athlete_id, active_only=True)
            activities = await self.supabase.get_recent_activities(athlete_id, limit=30)

            assessments = []
            for goal in running_goals:
                # Calculate current progress based on goal type
                progress = await self._calculate_goal_progress(goal, activities)

                # Update progress in database
                await self.supabase.update_running_goal_progress(goal.id, progress)

                # Generate AI assessment
                assessment = await self._generate_running_goal_assessment(goal, activities, progress)
                assessments.append(assessment)

            logger.info(f"Assessed {len(assessments)} running goals for athlete {athlete_id}")
            return assessments

        except Exception as e:
            logger.error(f"Enhanced goal assessment failed: {str(e)}")
            return []

    async def _calculate_goal_progress(
        self,
        goal: RunningGoal,
        activities: List[EnhancedActivity]
    ) -> float:
        """Calculate current progress toward a running goal"""
        try:
            if goal.goal_type == "weekly_mileage":
                # Calculate average weekly mileage
                total_distance = sum(float(a.distance) for a in activities)
                weeks = len(activities) / 7  # Rough estimate
                weekly_mileage = (total_distance / 1000) * 0.621371 / weeks if weeks > 0 else 0
                return weekly_mileage

            elif goal.goal_type == "distance":
                # Total distance accumulated
                total_distance = sum(float(a.distance) for a in activities)
                total_miles = (total_distance / 1000) * 0.621371
                return total_miles

            elif goal.goal_type == "consistency":
                # Percentage of days with activity
                days_with_activity = len(set(a.activity_date.date() for a in activities))
                total_days = 30  # Last 30 days
                consistency_percentage = (days_with_activity / total_days) * 100
                return consistency_percentage

            elif goal.goal_type == "race_time":
                # Estimate based on recent pace trends
                if activities:
                    # Get recent 5K equivalent pace
                    recent_paces = []
                    for a in activities[:5]:
                        if a.distance and a.moving_time:
                            miles = (float(a.distance) / 1000) * 0.621371
                            pace = a.moving_time / 60 / miles if miles > 0 else 0
                            recent_paces.append(pace)
                    if recent_paces:
                        avg_pace = sum(recent_paces) / len(recent_paces)
                        estimated_5k_time = avg_pace * 3.1  # 5K is 3.1 miles
                        return estimated_5k_time  # In minutes

            return float(goal.current_progress) if goal.current_progress else 0.0

        except Exception as e:
            logger.error(f"Failed to calculate goal progress: {e}")
            return 0.0

    async def _generate_running_goal_assessment(
        self,
        goal: RunningGoal,
        activities: List[EnhancedActivity],
        progress: float
    ) -> GoalAssessment:
        """Generate AI-powered assessment for a running goal"""
        try:
            if not self.client:
                return self._get_fallback_running_goal_assessment(goal, progress)

            # Calculate time remaining
            days_remaining = (goal.deadline - datetime.now()).days
            weeks_remaining = days_remaining / 7

            # Prepare context
            recent_activities_summary = self._format_activities_for_goal(activities[:10])

            prompt = f"""
As an expert running coach, assess this runner's goal progress:

GOAL DETAILS:
- Title: {goal.title}
- Type: {goal.goal_type}
- Target: {float(goal.target_value):.1f}
- Current Progress: {progress:.1f}
- Deadline: {goal.deadline.strftime('%Y-%m-%d')} ({days_remaining} days / {weeks_remaining:.1f} weeks remaining)
- Completion: {(progress / float(goal.target_value) * 100):.1f}%

RECENT ACTIVITIES (last 10):
{recent_activities_summary}

Please provide a JSON response with:
1. "current_status": One of "ON_TRACK", "BEHIND", "AHEAD", "NEEDS_ADJUSTMENT"
2. "feasibility_score": Float between 0-1 indicating how realistic the goal is
3. "recommendations": List of 3-5 specific, actionable recommendations
4. "timeline_adjustments": List of 2-3 insights about timeline and pacing
5. "key_insights": 2-3 critical insights about their progress

Focus on:
- Realistic assessment based on current progress and time remaining
- Specific, actionable advice
- Addressing gaps between current and target performance
- Use MILES for distance measurements

Respond in JSON format only.
"""

            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse AI response
            import json
            ai_content = response.content[0].text

            try:
                start = ai_content.find('{')
                end = ai_content.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = ai_content[start:end]
                    ai_data = json.loads(json_str)

                    return GoalAssessment(
                        goal_id=str(goal.id),
                        goal_type=self._determine_goal_type_from_string(goal.goal_type),
                        current_status=self._parse_goal_status(ai_data.get("current_status", "ON_TRACK")),
                        progress_percentage=(progress / float(goal.target_value)) * 100,
                        feasibility_score=float(ai_data.get("feasibility_score", 0.7)),
                        recommendations=ai_data.get("recommendations", []),
                        timeline_adjustments=ai_data.get("timeline_adjustments", []),
                        key_metrics=self._extract_running_goal_metrics(goal, activities, progress)
                    )
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")

            return self._get_fallback_running_goal_assessment(goal, progress)

        except Exception as e:
            logger.error(f"AI goal assessment failed: {str(e)}")
            return self._get_fallback_running_goal_assessment(goal, progress)

    def _format_activities_for_goal(self, activities: List[EnhancedActivity]) -> str:
        """Format activities for goal assessment prompt"""
        if not activities:
            return "No recent activities"

        lines = []
        for a in activities:
            distance_miles = (float(a.distance) / 1000) * 0.621371
            pace = (a.moving_time / 60 / distance_miles) if distance_miles > 0 else 0
            pace_str = f"{int(pace)}:{int((pace % 1) * 60):02d}/mile" if pace > 0 else "N/A"
            lines.append(
                f"- {a.activity_date.strftime('%Y-%m-%d')}: {distance_miles:.1f} miles at {pace_str}"
            )

        return "\n".join(lines)

    def _determine_goal_type_from_string(self, goal_type_str: str) -> GoalType:
        """Convert string goal type to enum"""
        mapping = {
            "race_time": GoalType.RACE_TIME,
            "distance": GoalType.DISTANCE,
            "consistency": GoalType.CONSISTENCY,
            "weekly_mileage": GoalType.DISTANCE,
            "weight_loss": GoalType.WEIGHT_LOSS,
            "general_fitness": GoalType.GENERAL_FITNESS,
        }
        return mapping.get(goal_type_str.lower(), GoalType.GENERAL_FITNESS)

    def _extract_running_goal_metrics(
        self,
        goal: RunningGoal,
        activities: List[EnhancedActivity],
        progress: float
    ) -> Dict[str, Any]:
        """Extract key metrics for running goal assessment"""
        metrics = {
            "goal_type": goal.goal_type,
            "target_value": float(goal.target_value),
            "current_progress": progress,
            "completion_percentage": (progress / float(goal.target_value)) * 100,
            "days_remaining": (goal.deadline - datetime.now()).days,
            "is_completed": goal.is_completed
        }

        # Add goal-specific metrics
        if goal.goal_type == "race_time":
            # Calculate current estimated race time
            if activities:
                recent_paces = []
                for a in activities[:5]:
                    if a.distance and a.moving_time:
                        miles = (float(a.distance) / 1000) * 0.621371
                        pace = a.moving_time / 60 / miles if miles > 0 else 0
                        recent_paces.append(pace)
                if recent_paces:
                    avg_pace = sum(recent_paces) / len(recent_paces)
                    metrics["current_pace"] = f"{int(avg_pace)}:{int((avg_pace % 1) * 60):02d}"
                    metrics["target_pace"] = "Calculate based on target"

        elif goal.goal_type == "weekly_mileage":
            if activities:
                total_distance = sum(float(a.distance) for a in activities)
                weeks = len(activities) / 7
                weekly_mileage = (total_distance / 1000) * 0.621371 / weeks if weeks > 0 else 0
                metrics["current_weekly_mileage"] = weekly_mileage
                metrics["target_weekly_mileage"] = float(goal.target_value)

        return metrics

    def _get_fallback_running_goal_assessment(
        self,
        goal: RunningGoal,
        progress: float
    ) -> GoalAssessment:
        """Fallback assessment when AI is not available"""
        completion_pct = (progress / float(goal.target_value)) * 100 if goal.target_value else 0

        # Determine status based on completion percentage
        if completion_pct >= 90:
            status = GoalStatus.AHEAD
        elif completion_pct >= 60:
            status = GoalStatus.ON_TRACK
        elif completion_pct >= 30:
            status = GoalStatus.BEHIND
        else:
            status = GoalStatus.NEEDS_ADJUSTMENT

        return GoalAssessment(
            goal_id=str(goal.id),
            goal_type=self._determine_goal_type_from_string(goal.goal_type),
            current_status=status,
            progress_percentage=completion_pct,
            feasibility_score=0.7,
            recommendations=[
                "Continue current training consistency",
                "Monitor progress weekly",
                "Adjust training volume as needed"
            ],
            timeline_adjustments=[
                f"Goal is {completion_pct:.1f}% complete",
                f"{(goal.deadline - datetime.now()).days} days remaining"
            ],
            key_metrics=self._extract_running_goal_metrics(goal, [], progress)
        )

    async def track_daily_commitments(self, athlete_id: int) -> Dict[str, Any]:
        """Track streak maintenance and daily commitment fulfillment"""
        if not self.supabase:
            logger.error("Supabase queries not initialized")
            return {}

        try:
            commitments = await self.supabase.get_daily_commitments(athlete_id, days=30)

            # Calculate current streak
            current_streak = await self.supabase.calculate_streak(athlete_id)

            # Calculate fulfillment rate
            fulfilled_count = sum(1 for c in commitments if c.is_fulfilled)
            fulfillment_rate = fulfilled_count / len(commitments) if commitments else 0

            # Find longest streak
            longest_streak = self._calculate_longest_streak(commitments)

            return {
                "current_streak": current_streak,
                "fulfillment_rate": fulfillment_rate,
                "longest_streak": longest_streak,
                "total_commitments": len(commitments),
                "fulfilled_commitments": fulfilled_count,
                "recommendations": self._generate_commitment_recommendations(
                    current_streak, fulfillment_rate
                )
            }

        except Exception as e:
            logger.error(f"Failed to track daily commitments: {e}")
            return {}

    def _calculate_longest_streak(self, commitments: List[DailyCommitment]) -> int:
        """Calculate longest fulfillment streak"""
        if not commitments:
            return 0

        # Sort by date
        sorted_commitments = sorted(commitments, key=lambda c: c.commitment_date)

        longest = 0
        current = 0
        prev_date = None

        for commitment in sorted_commitments:
            if commitment.is_fulfilled:
                if prev_date is None or (commitment.commitment_date - prev_date).days == 1:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1
                prev_date = commitment.commitment_date
            else:
                current = 0
                prev_date = None

        return longest

    def _generate_commitment_recommendations(
        self,
        current_streak: int,
        fulfillment_rate: float
    ) -> List[str]:
        """Generate recommendations for daily commitment tracking"""
        recommendations = []

        if current_streak == 0:
            recommendations.append("Start a new streak today - consistency is key!")
        elif current_streak < 7:
            recommendations.append(f"Great start! Keep your {current_streak}-day streak going")
        elif current_streak < 30:
            recommendations.append(f"Excellent {current_streak}-day streak! Aim for 30 days")
        else:
            recommendations.append(f"Amazing {current_streak}-day streak! You're building strong habits")

        if fulfillment_rate < 0.5:
            recommendations.append("Try to fulfill at least 50% of your commitments")
        elif fulfillment_rate < 0.7:
            recommendations.append("Good progress - aim for 70%+ fulfillment rate")
        elif fulfillment_rate < 0.9:
            recommendations.append("Excellent fulfillment rate - keep it up!")
        else:
            recommendations.append("Outstanding consistency - you're crushing your commitments!")

        return recommendations