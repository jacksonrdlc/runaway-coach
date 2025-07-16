from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class WorkoutType(Enum):
    EASY_RUN = "easy_run"
    TEMPO_RUN = "tempo_run"
    INTERVAL_TRAINING = "interval_training"
    LONG_RUN = "long_run"
    RECOVERY_RUN = "recovery_run"

class Activity(BaseModel):
    id: str
    type: str
    distance: float
    duration: int
    avg_pace: str
    date: datetime
    heart_rate_avg: Optional[int] = None
    elevation_gain: Optional[float] = None

class RunnerProfile(BaseModel):
    user_id: str
    age: int
    gender: str
    experience_level: str
    weekly_mileage: float
    best_times: Dict[str, str]
    preferences: Dict[str, Any]

class WorkoutData(BaseModel):
    activity: Activity
    planned_workout: Optional[Dict[str, Any]] = None
    runner_profile: RunnerProfile

class WorkoutInsights(BaseModel):
    performance_rating: float
    effort_level: str
    recommendations: List[str]
    next_workout_suggestions: List[str]

class WorkoutFeedbackResponse(BaseModel):
    success: bool
    insights: Optional[WorkoutInsights] = None
    error_message: Optional[str] = None
    processing_time: float

class AgenticAnalysis(BaseModel):
    performance_metrics: Dict[str, Any]
    recommendations: List[str]
    agent_metadata: Dict[str, Any]

class AnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[AgenticAnalysis] = None
    error_message: Optional[str] = None
    processing_time: float

__all__ = [
    "WorkoutType",
    "Activity", 
    "RunnerProfile",
    "WorkoutData",
    "WorkoutInsights",
    "WorkoutFeedbackResponse",
    "AgenticAnalysis",
    "AnalysisResponse"
]