"""
Supabase Query Integration Layer

Provides type-safe queries for Strava data from Supabase database.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from supabase import Client

from models.strava import (
    Athlete, AthleteStats, EnhancedActivity, ActivityType,
    Gear, Brand, Model, Route, Segment,
    StarredRoute, StarredSegment,
    RunningGoal, StravaGoal, DailyCommitment,
    Follow, Comment, Reaction,
    Club, Membership,
    Challenge, ChallengeParticipation,
    Media, ConnectedApp, Login, Contact
)

logger = logging.getLogger(__name__)


class SupabaseQueries:
    """Type-safe Supabase queries for Strava data"""

    def __init__(self, client: Client):
        self.client = client

    # =====================================
    # Athlete Queries
    # =====================================

    async def get_athlete(self, auth_user_id: str) -> Optional[Athlete]:
        """Get athlete by auth_user_id"""
        try:
            response = self.client.table("athletes")\
                .select("*")\
                .eq("auth_user_id", auth_user_id)\
                .single()\
                .execute()
            return Athlete(**response.data) if response.data else None
        except Exception as e:
            logger.error(f"Failed to get athlete: {e}")
            return None

    async def get_athlete_by_id(self, athlete_id: int) -> Optional[Athlete]:
        """Get athlete by athlete_id"""
        try:
            response = self.client.table("athletes")\
                .select("*")\
                .eq("id", athlete_id)\
                .single()\
                .execute()
            return Athlete(**response.data) if response.data else None
        except Exception as e:
            logger.error(f"Failed to get athlete by id: {e}")
            return None

    async def get_athlete_stats(self, athlete_id: int) -> Optional[AthleteStats]:
        """Get aggregated athlete statistics"""
        try:
            response = self.client.table("athlete_stats")\
                .select("*")\
                .eq("athlete_id", athlete_id)\
                .single()\
                .execute()
            return AthleteStats(**response.data) if response.data else None
        except Exception as e:
            logger.error(f"Failed to get athlete stats: {e}")
            return None

    # =====================================
    # Activity Queries
    # =====================================

    async def get_recent_activities(
        self,
        athlete_id: int,
        limit: int = 30,
        activity_type: Optional[str] = None
    ) -> List[EnhancedActivity]:
        """Get recent activities with all fields"""
        try:
            query = self.client.table("activities")\
                .select("*")\
                .eq("athlete_id", athlete_id)\
                .order("activity_date", desc=True)\
                .limit(limit)

            if activity_type:
                query = query.eq("activity_type_id", activity_type)

            response = query.execute()
            return [EnhancedActivity(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get recent activities: {e}")
            return []

    async def get_activities_by_date_range(
        self,
        athlete_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[EnhancedActivity]:
        """Get activities within a date range"""
        try:
            response = self.client.table("activities")\
                .select("*")\
                .eq("athlete_id", athlete_id)\
                .gte("activity_date", start_date.isoformat())\
                .lte("activity_date", end_date.isoformat())\
                .order("activity_date", desc=True)\
                .execute()
            return [EnhancedActivity(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get activities by date range: {e}")
            return []

    async def get_activity_by_id(self, activity_id: int) -> Optional[EnhancedActivity]:
        """Get single activity by ID"""
        try:
            response = self.client.table("activities")\
                .select("*")\
                .eq("id", activity_id)\
                .single()\
                .execute()
            return EnhancedActivity(**response.data) if response.data else None
        except Exception as e:
            logger.error(f"Failed to get activity: {e}")
            return None

    async def get_activity_types(self) -> List[ActivityType]:
        """Get all activity types"""
        try:
            response = self.client.table("activity_types")\
                .select("*")\
                .execute()
            return [ActivityType(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get activity types: {e}")
            return []

    # =====================================
    # Gear Queries
    # =====================================

    async def get_athlete_gear(
        self,
        athlete_id: int,
        gear_type: Optional[str] = None
    ) -> List[Gear]:
        """Get athlete's gear, optionally filtered by type"""
        try:
            query = self.client.table("gear")\
                .select("*")\
                .eq("athlete_id", athlete_id)

            if gear_type:
                query = query.eq("gear_type", gear_type)

            response = query.order("total_distance", desc=True).execute()
            return [Gear(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get athlete gear: {e}")
            return []

    async def get_gear_by_id(self, gear_id: int) -> Optional[Gear]:
        """Get specific gear by ID"""
        try:
            response = self.client.table("gear")\
                .select("*")\
                .eq("id", gear_id)\
                .single()\
                .execute()
            return Gear(**response.data) if response.data else None
        except Exception as e:
            logger.error(f"Failed to get gear: {e}")
            return None

    async def get_brands(self) -> List[Brand]:
        """Get all gear brands"""
        try:
            response = self.client.table("brands").select("*").execute()
            return [Brand(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get brands: {e}")
            return []

    async def get_models_by_brand(self, brand_id: int) -> List[Model]:
        """Get models for a specific brand"""
        try:
            response = self.client.table("models")\
                .select("*")\
                .eq("brand_id", brand_id)\
                .execute()
            return [Model(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []

    # =====================================
    # Goal Queries
    # =====================================

    async def get_running_goals(
        self,
        athlete_id: int,
        active_only: bool = True
    ) -> List[RunningGoal]:
        """Get app-specific running goals"""
        try:
            query = self.client.table("running_goals")\
                .select("*")\
                .eq("athlete_id", athlete_id)

            if active_only:
                query = query.eq("is_active", True)

            response = query.order("created_at", desc=True).execute()
            return [RunningGoal(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get running goals: {e}")
            return []

    async def get_running_goal(self, goal_id: int) -> Optional[RunningGoal]:
        """Get specific running goal by ID"""
        try:
            response = self.client.table("running_goals")\
                .select("*")\
                .eq("id", goal_id)\
                .single()\
                .execute()
            return RunningGoal(**response.data) if response.data else None
        except Exception as e:
            logger.error(f"Failed to get running goal: {e}")
            return None

    async def update_running_goal_progress(
        self,
        goal_id: int,
        progress: float
    ) -> bool:
        """Update goal progress and check completion"""
        try:
            goal = await self.get_running_goal(goal_id)
            if not goal:
                return False

            update_data: Dict[str, Any] = {
                "current_progress": progress,
                "updated_at": datetime.now().isoformat()
            }

            # Check if goal is completed
            if progress >= float(goal.target_value) and not goal.is_completed:
                update_data.update({
                    "is_completed": True,
                    "completed_at": datetime.now().isoformat(),
                    "is_active": False
                })
                logger.info(f"Goal {goal_id} marked as completed!")

            self.client.table("running_goals")\
                .update(update_data)\
                .eq("id", goal_id)\
                .execute()

            return True
        except Exception as e:
            logger.error(f"Failed to update running goal progress: {e}")
            return False

    async def create_running_goal(
        self,
        athlete_id: int,
        title: str,
        goal_type: str,
        target_value: float,
        deadline: datetime
    ) -> Optional[RunningGoal]:
        """Create a new running goal"""
        try:
            response = self.client.table("running_goals").insert({
                "athlete_id": athlete_id,
                "title": title,
                "goal_type": goal_type,
                "target_value": target_value,
                "deadline": deadline.isoformat(),
                "is_active": True,
                "is_completed": False,
                "current_progress": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()
            return RunningGoal(**response.data[0]) if response.data else None
        except Exception as e:
            logger.error(f"Failed to create running goal: {e}")
            return None

    async def get_strava_goals(self, athlete_id: int) -> List[StravaGoal]:
        """Get Strava's native goals"""
        try:
            response = self.client.table("goals")\
                .select("*")\
                .eq("athlete_id", athlete_id)\
                .execute()
            return [StravaGoal(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get Strava goals: {e}")
            return []

    # =====================================
    # Daily Commitment Queries
    # =====================================

    async def get_daily_commitments(
        self,
        athlete_id: int,
        days: int = 30
    ) -> List[DailyCommitment]:
        """Get daily commitments for the last N days"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).date()
            response = self.client.table("daily_commitments")\
                .select("*")\
                .eq("athlete_id", athlete_id)\
                .gte("commitment_date", start_date.isoformat())\
                .order("commitment_date", desc=True)\
                .execute()
            return [DailyCommitment(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get daily commitments: {e}")
            return []

    async def create_daily_commitment(
        self,
        athlete_id: int,
        commitment_date: date,
        activity_type: str
    ) -> Optional[DailyCommitment]:
        """Create a new daily commitment"""
        try:
            response = self.client.table("daily_commitments").insert({
                "athlete_id": athlete_id,
                "commitment_date": commitment_date.isoformat(),
                "activity_type": activity_type,
                "is_fulfilled": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()
            return DailyCommitment(**response.data[0]) if response.data else None
        except Exception as e:
            logger.error(f"Failed to create daily commitment: {e}")
            return None

    async def fulfill_daily_commitment(
        self,
        commitment_id: int
    ) -> bool:
        """Mark a daily commitment as fulfilled"""
        try:
            self.client.table("daily_commitments").update({
                "is_fulfilled": True,
                "fulfilled_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).eq("id", commitment_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to fulfill daily commitment: {e}")
            return False

    # =====================================
    # Segment & Route Queries
    # =====================================

    async def get_starred_segments(self, athlete_id: int) -> List[Segment]:
        """Get athlete's starred segments with details"""
        try:
            response = self.client.table("starred_segments")\
                .select("segment_id, segments(*)")\
                .eq("athlete_id", athlete_id)\
                .execute()

            segments = []
            for row in response.data:
                if row.get('segments'):
                    segments.append(Segment(**row['segments']))
            return segments
        except Exception as e:
            logger.error(f"Failed to get starred segments: {e}")
            return []

    async def get_starred_routes(self, athlete_id: int) -> List[Route]:
        """Get athlete's starred routes with details"""
        try:
            response = self.client.table("starred_routes")\
                .select("route_id, routes(*)")\
                .eq("athlete_id", athlete_id)\
                .execute()

            routes = []
            for row in response.data:
                if row.get('routes'):
                    routes.append(Route(**row['routes']))
            return routes
        except Exception as e:
            logger.error(f"Failed to get starred routes: {e}")
            return []

    async def get_segments_for_activity(self, activity_id: int) -> List[Segment]:
        """Get all segments for a specific activity"""
        try:
            response = self.client.table("segments")\
                .select("*")\
                .eq("activity_id", activity_id)\
                .execute()
            return [Segment(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get segments for activity: {e}")
            return []

    # =====================================
    # Social Queries
    # =====================================

    async def get_followers(self, athlete_id: int) -> List[Follow]:
        """Get athlete's followers"""
        try:
            response = self.client.table("follows")\
                .select("*")\
                .eq("following_id", athlete_id)\
                .execute()
            return [Follow(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get followers: {e}")
            return []

    async def get_following(self, athlete_id: int) -> List[Follow]:
        """Get athletes that this athlete follows"""
        try:
            response = self.client.table("follows")\
                .select("*")\
                .eq("follower_id", athlete_id)\
                .execute()
            return [Follow(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get following: {e}")
            return []

    async def get_activity_comments(self, activity_id: int) -> List[Comment]:
        """Get comments for an activity"""
        try:
            response = self.client.table("comments")\
                .select("*")\
                .eq("activity_id", activity_id)\
                .order("comment_date", desc=True)\
                .execute()
            return [Comment(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get activity comments: {e}")
            return []

    async def get_activity_reactions(self, activity_id: int) -> List[Reaction]:
        """Get reactions for an activity"""
        try:
            response = self.client.table("reactions")\
                .select("*")\
                .eq("parent_type", "activity")\
                .eq("parent_id", activity_id)\
                .execute()
            return [Reaction(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to get activity reactions: {e}")
            return []

    # =====================================
    # Club & Challenge Queries
    # =====================================

    async def get_athlete_clubs(self, athlete_id: int) -> List[Club]:
        """Get clubs that athlete is a member of"""
        try:
            response = self.client.table("memberships")\
                .select("club_id, clubs(*)")\
                .eq("athlete_id", athlete_id)\
                .execute()

            clubs = []
            for row in response.data:
                if row.get('clubs'):
                    clubs.append(Club(**row['clubs']))
            return clubs
        except Exception as e:
            logger.error(f"Failed to get athlete clubs: {e}")
            return []

    async def get_athlete_challenges(
        self,
        athlete_id: int,
        active_only: bool = True
    ) -> List[Challenge]:
        """Get challenges athlete is participating in"""
        try:
            query = self.client.table("challenge_participations")\
                .select("challenge_id, challenges(*)")\
                .eq("athlete_id", athlete_id)

            if active_only:
                query = query.eq("completed", False)

            response = query.execute()

            challenges = []
            for row in response.data:
                if row.get('challenges'):
                    challenges.append(Challenge(**row['challenges']))
            return challenges
        except Exception as e:
            logger.error(f"Failed to get athlete challenges: {e}")
            return []

    # =====================================
    # Utility Methods
    # =====================================

    async def calculate_streak(self, athlete_id: int) -> int:
        """Calculate current activity streak in days"""
        try:
            commitments = await self.get_daily_commitments(athlete_id, days=365)
            if not commitments:
                return 0

            # Sort by date descending
            commitments.sort(key=lambda c: c.commitment_date, reverse=True)

            streak = 0
            current_date = date.today()

            for commitment in commitments:
                if commitment.commitment_date == current_date and commitment.is_fulfilled:
                    streak += 1
                    current_date -= timedelta(days=1)
                elif commitment.commitment_date < current_date:
                    break

            return streak
        except Exception as e:
            logger.error(f"Failed to calculate streak: {e}")
            return 0

    async def get_weekly_mileage(
        self,
        athlete_id: int,
        weeks: int = 1
    ) -> float:
        """Calculate weekly mileage for the last N weeks"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks)

            activities = await self.get_activities_by_date_range(
                athlete_id, start_date, end_date
            )

            total_distance_meters = sum(float(a.distance) for a in activities)
            total_distance_miles = (total_distance_meters / 1000) * 0.621371

            return total_distance_miles / weeks  # Average per week
        except Exception as e:
            logger.error(f"Failed to calculate weekly mileage: {e}")
            return 0.0


# Export
__all__ = ["SupabaseQueries"]