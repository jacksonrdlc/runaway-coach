from typing import Dict, Any, List
import logging
import os
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

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
        logger.info("GoalStrategyAgent initialized")
    
    async def assess_goals(self, goals_data: List[Dict[str, Any]], 
                          activities_data: List[Dict[str, Any]]) -> List[GoalAssessment]:
        """Assess goal feasibility and progress"""
        try:
            assessments = []
            
            for i, goal in enumerate(goals_data):
                # Mock goal assessment
                assessment = GoalAssessment(
                    goal_id=goal.get("id", f"goal_{i}"),
                    goal_type=GoalType.RACE_TIME,
                    current_status=GoalStatus.ON_TRACK,
                    progress_percentage=65.0,
                    feasibility_score=0.8,
                    recommendations=[
                        "Increase weekly mileage by 15%",
                        "Add one tempo run per week",
                        "Focus on race pace intervals"
                    ],
                    timeline_adjustments=[
                        "Goal is achievable in current timeline",
                        "Consider adding 2 weeks for optimal preparation"
                    ],
                    key_metrics={
                        "current_pace": "8:15",
                        "target_pace": "7:45",
                        "weekly_mileage": 25.0,
                        "target_mileage": 35.0
                    }
                )
                assessments.append(assessment)
            
            logger.info(f"Goal assessment completed for {len(goals_data)} goals")
            return assessments
            
        except Exception as e:
            logger.error(f"Goal assessment failed: {str(e)}")
            raise
    
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