from typing import Dict, Any, List
import logging
import os
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class PaceType(Enum):
    EASY = "easy"
    TEMPO = "tempo"
    THRESHOLD = "threshold"
    INTERVAL = "interval"
    RACE = "race"

@dataclass
class PaceRecommendation:
    pace_type: PaceType
    target_pace: str
    pace_range: str
    description: str
    heart_rate_zone: str

@dataclass
class PaceOptimization:
    current_fitness_level: str
    recommended_paces: List[PaceRecommendation]
    weekly_pace_distribution: Dict[str, float]
    improvement_targets: List[str]

class PaceOptimizationAgent:
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
        logger.info("PaceOptimizationAgent initialized")
    
    async def optimize_paces(self, activities_data: List[Dict[str, Any]]) -> PaceOptimization:
        """Optimize paces based on recent performance data"""
        try:
            # Mock pace optimization
            recommended_paces = [
                PaceRecommendation(
                    pace_type=PaceType.EASY,
                    target_pace="8:45",
                    pace_range="8:30-9:00",
                    description="Conversational pace for base building",
                    heart_rate_zone="Zone 2"
                ),
                PaceRecommendation(
                    pace_type=PaceType.TEMPO,
                    target_pace="7:30",
                    pace_range="7:15-7:45",
                    description="Comfortably hard, sustainable pace",
                    heart_rate_zone="Zone 3-4"
                ),
                PaceRecommendation(
                    pace_type=PaceType.INTERVAL,
                    target_pace="6:45",
                    pace_range="6:30-7:00",
                    description="Hard effort for speed development",
                    heart_rate_zone="Zone 4-5"
                ),
                PaceRecommendation(
                    pace_type=PaceType.RACE,
                    target_pace="7:00",
                    pace_range="6:50-7:10",
                    description="Target race pace for 10K",
                    heart_rate_zone="Zone 4"
                )
            ]
            
            optimization = PaceOptimization(
                current_fitness_level="Intermediate",
                recommended_paces=recommended_paces,
                weekly_pace_distribution={
                    "easy": 0.7,
                    "tempo": 0.2,
                    "interval": 0.1
                },
                improvement_targets=[
                    "Improve lactate threshold by 10 seconds per mile",
                    "Increase aerobic capacity",
                    "Maintain consistent pacing"
                ]
            )
            
            logger.info(f"Pace optimization completed for {len(activities_data)} activities")
            return optimization
            
        except Exception as e:
            logger.error(f"Pace optimization failed: {str(e)}")
            raise