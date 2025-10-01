"""
Strava Data Models

Pydantic models matching the Strava ERD schema for complete data representation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class Athlete(BaseModel):
    """Athlete profile from Strava"""
    id: int
    auth_user_id: str  # UUID from Supabase auth
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[Decimal] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime


class AthleteStats(BaseModel):
    """Aggregated lifetime statistics for athlete"""
    id: int
    athlete_id: int
    count: int  # Total activities
    distance: Decimal  # Total distance (meters)
    moving_time: int  # Total moving time (seconds)
    elapsed_time: int  # Total elapsed time (seconds)
    elevation_gain: Decimal  # Total elevation gain (meters)
    achievement_count: int
    ytd_distance: Decimal  # Year-to-date distance (meters)
    created_at: datetime
    updated_at: datetime


class ActivityType(BaseModel):
    """Activity type reference data"""
    id: int
    name: str
    category: str
    description: Optional[str] = None


class EnhancedActivity(BaseModel):
    """Fully expanded Strava activity with all available metrics"""
    id: int
    athlete_id: int
    activity_type_id: int
    name: str
    description: Optional[str] = None
    activity_date: datetime
    elapsed_time: int  # seconds
    moving_time: int  # seconds
    distance: Decimal  # meters

    # Elevation data
    elevation_gain: Optional[Decimal] = None
    elevation_loss: Optional[Decimal] = None
    elevation_low: Optional[Decimal] = None
    elevation_high: Optional[Decimal] = None

    # Speed metrics
    max_speed: Optional[Decimal] = None
    average_speed: Optional[Decimal] = None

    # Heart rate
    max_heart_rate: Optional[int] = None
    average_heart_rate: Optional[int] = None

    # Power metrics (for runners with power meters)
    max_watts: Optional[int] = None
    average_watts: Optional[int] = None
    weighted_average_watts: Optional[int] = None

    # Cadence
    max_cadence: Optional[int] = None
    average_cadence: Optional[int] = None

    # Other metrics
    calories: Optional[int] = None

    # Weather data
    max_temperature: Optional[Decimal] = None
    average_temperature: Optional[Decimal] = None
    weather_condition: Optional[str] = None
    humidity: Optional[Decimal] = None
    wind_speed: Optional[Decimal] = None

    # Geographic data
    map_polyline: Optional[str] = None
    map_summary_polyline: Optional[str] = None
    start_latitude: Optional[Decimal] = None
    start_longitude: Optional[Decimal] = None
    end_latitude: Optional[Decimal] = None
    end_longitude: Optional[Decimal] = None

    # Flags
    commute: bool = False
    flagged: bool = False
    with_pet: bool = False
    competition: bool = False

    # Relations
    gear_id: Optional[int] = None
    filename: Optional[str] = None
    created_at: datetime


class Brand(BaseModel):
    """Gear brand reference data"""
    id: int
    name: str
    description: Optional[str] = None


class Model(BaseModel):
    """Gear model reference data"""
    id: int
    brand_id: int
    name: str
    category: str


class Gear(BaseModel):
    """Athlete's gear (shoes, bikes, etc)"""
    id: int
    athlete_id: int
    brand_id: Optional[int] = None
    model_id: Optional[int] = None
    gear_type: str  # "shoes", "bike", etc
    name: str
    is_primary: bool = False
    total_distance: int  # meters
    created_at: datetime


class Route(BaseModel):
    """Saved route"""
    id: int
    athlete_id: int
    name: str
    filename: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class Segment(BaseModel):
    """Segment from an activity"""
    id: int
    activity_id: int
    name: str
    start_latitude: Decimal
    start_longitude: Decimal
    end_latitude: Decimal
    end_longitude: Decimal
    created_at: datetime


class StarredRoute(BaseModel):
    """Athlete's starred routes"""
    athlete_id: int
    route_id: int
    starred_at: datetime


class StarredSegment(BaseModel):
    """Athlete's starred segments"""
    athlete_id: int
    segment_id: int
    starred_at: datetime


class Follow(BaseModel):
    """Social follow relationship"""
    follower_id: int
    following_id: int
    status: str
    is_favorite: bool = False
    created_at: datetime


class Comment(BaseModel):
    """Comment on an activity"""
    id: int
    activity_id: int
    athlete_id: int
    content: str
    comment_date: datetime


class Reaction(BaseModel):
    """Reaction to activity or comment"""
    id: int
    parent_type: str  # "activity" or "comment"
    parent_id: int
    athlete_id: int
    reaction_type: str  # "like", "kudos", etc
    reaction_date: datetime


class Club(BaseModel):
    """Running/cycling club"""
    id: int
    name: str
    description: Optional[str] = None
    club_type: str
    sport: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    cover_photo: Optional[str] = None
    club_picture: Optional[str] = None
    created_at: datetime


class Membership(BaseModel):
    """Club membership"""
    athlete_id: int
    club_id: int
    join_date: datetime
    status: str


class Challenge(BaseModel):
    """Strava challenge"""
    id: int
    name: str
    challenge_type: str
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None


class ChallengeParticipation(BaseModel):
    """Athlete's participation in a challenge"""
    athlete_id: int
    challenge_id: int
    join_date: datetime
    completed: bool = False
    completion_date: Optional[datetime] = None


class StravaGoal(BaseModel):
    """Strava's native goals (from Strava export)"""
    id: int
    athlete_id: int
    goal_type: str
    activity_type: str
    target_value: Decimal
    start_date: datetime
    end_date: datetime
    segment_id: Optional[int] = None
    time_period: str  # "weekly", "monthly", "yearly"
    interval_time: Optional[int] = None


class RunningGoal(BaseModel):
    """App-specific running goals with progress tracking"""
    id: int
    athlete_id: int
    title: str
    goal_type: str  # "race_time", "distance", "consistency", "weekly_mileage"
    target_value: Decimal
    deadline: datetime
    is_active: bool = True
    is_completed: bool = False
    current_progress: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class DailyCommitment(BaseModel):
    """Daily commitment tracking for streaks"""
    id: int
    athlete_id: int
    commitment_date: date
    activity_type: str
    is_fulfilled: bool = False
    fulfilled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class Media(BaseModel):
    """Media attached to activities"""
    id: int
    activity_id: int
    filename: str
    caption: Optional[str] = None
    media_type: str
    created_at: datetime


class ConnectedApp(BaseModel):
    """Connected third-party apps"""
    id: int
    athlete_id: int
    app_name: str
    enabled: bool = True
    connected_at: datetime


class Login(BaseModel):
    """Login history"""
    id: int
    athlete_id: int
    ip_address: Optional[str] = None
    login_source: Optional[str] = None
    login_datetime: datetime


class Contact(BaseModel):
    """Athlete contacts"""
    id: int
    athlete_id: int
    contact_athlete_id: Optional[int] = None
    contact_type: str
    contact_value: str
    contact_source: Optional[str] = None
    contact_name: Optional[str] = None


# Export all models
__all__ = [
    "Athlete",
    "AthleteStats",
    "ActivityType",
    "EnhancedActivity",
    "Brand",
    "Model",
    "Gear",
    "Route",
    "Segment",
    "StarredRoute",
    "StarredSegment",
    "Follow",
    "Comment",
    "Reaction",
    "Club",
    "Membership",
    "Challenge",
    "ChallengeParticipation",
    "StravaGoal",
    "RunningGoal",
    "DailyCommitment",
    "Media",
    "ConnectedApp",
    "Login",
    "Contact",
]