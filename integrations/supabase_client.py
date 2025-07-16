from supabase import create_client, Client
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..models import Activity, RunnerProfile, GoalModel
from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SupabaseClient:
    """Client for interacting with Supabase database"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    async def get_user_activities(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Activity]:
        """Fetch user activities from Supabase"""
        try:
            query = self.client.table("activities_with_maps").select(
                "id, name, type, summary_polyline, distance, start_date, elapsed_time"
            ).eq("user_id", user_id).order("start_date", desc=True).limit(limit)
            
            if start_date:
                query = query.gte("start_date", start_date.isoformat())
            
            result = query.execute()
            
            activities = []
            for row in result.data:
                try:
                    activity = Activity(
                        id=row["id"],
                        name=row.get("name"),
                        type=row.get("type"),
                        summary_polyline=row.get("summary_polyline"),
                        distance=row.get("distance"),
                        start_date=datetime.fromisoformat(row["start_date"].replace('Z', '+00:00')) if row.get("start_date") else None,
                        elapsed_time=row.get("elapsed_time")
                    )
                    activities.append(activity)
                except Exception as e:
                    logger.warning(f"Failed to parse activity {row.get('id', 'unknown')}: {str(e)}")
                    continue
            
            return activities
            
        except Exception as e:
            logger.error(f"Failed to fetch activities for user {user_id}: {str(e)}")
            return []
    
    async def get_user_goals(self, user_id: int) -> List[GoalModel]:
        """Fetch user goals from Supabase"""
        try:
            result = self.client.table("running_goals").select("*").eq(
                "user_id", user_id
            ).eq("is_active", True).execute()
            
            goals = []
            for row in result.data:
                try:
                    goal = GoalModel(
                        id=row["id"],
                        user_id=row["user_id"],
                        type=row["goal_type"],
                        target_value=row["target_value"],
                        deadline=datetime.fromisoformat(row["deadline"].replace('Z', '+00:00')),
                        created_date=datetime.fromisoformat(row["created_at"].replace('Z', '+00:00')),
                        updated_date=datetime.fromisoformat(row["updated_at"].replace('Z', '+00:00')) if row.get("updated_at") else None,
                        title=row["title"],
                        is_active=row["is_active"],
                        is_completed=row["is_completed"],
                        current_progress=row.get("current_progress", 0.0),
                        completed_date=datetime.fromisoformat(row["completed_at"].replace('Z', '+00:00')) if row.get("completed_at") else None
                    )
                    goals.append(goal)
                except Exception as e:
                    logger.warning(f"Failed to parse goal {row.get('id', 'unknown')}: {str(e)}")
                    continue
            
            return goals
            
        except Exception as e:
            logger.error(f"Failed to fetch goals for user {user_id}: {str(e)}")
            return []
    
    async def get_user_profile(self, user_id: int) -> Optional[RunnerProfile]:
        """Fetch user profile from Supabase"""
        try:
            # Get from profiles table
            profile_result = self.client.table("profiles").select("*").eq("user_id", user_id).execute()
            
            if not profile_result.data:
                return None
            
            profile_data = profile_result.data[0]
            
            # Get athlete info
            athlete_result = self.client.table("athletes").select("*").eq("user_id", user_id).execute()
            athlete_data = athlete_result.data[0] if athlete_result.data else {}
            
            return RunnerProfile(
                user_id=profile_data["user_id"],
                auth_id=profile_data["auth_id"],
                created_at=datetime.fromisoformat(profile_data["created_at"].replace('Z', '+00:00')) if profile_data.get("created_at") else None,
                updated_at=datetime.fromisoformat(profile_data["updated_at"].replace('Z', '+00:00')) if profile_data.get("updated_at") else None,
                firstname=athlete_data.get("firstname"),
                lastname=athlete_data.get("lastname"),
                city=athlete_data.get("city"),
                state=athlete_data.get("state"),
                country=athlete_data.get("country"),
                weight=athlete_data.get("weight")
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch profile for user {user_id}: {str(e)}")
            return None