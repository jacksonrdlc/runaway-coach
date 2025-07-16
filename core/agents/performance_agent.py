from typing import Dict, Any, List
import logging
import os
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class PerformanceTrend(Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"

@dataclass
class PerformanceMetrics:
    weekly_mileage: float
    recent_trend: PerformanceTrend
    consistency: float
    avg_pace: str

@dataclass
class PerformanceAnalysis:
    metrics: PerformanceMetrics
    strengths: List[str]
    recommendations: List[str]
    analysis_date: str

class PerformanceAnalysisAgent:
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
        logger.info("PerformanceAnalysisAgent initialized")
    
    async def analyze_performance(self, activities_data: List[Dict[str, Any]]) -> PerformanceAnalysis:
        """Analyze performance trends from activities data"""
        try:
            # Mock analysis for now
            metrics = PerformanceMetrics(
                weekly_mileage=25.0,
                recent_trend=PerformanceTrend.IMPROVING,
                consistency=0.8,
                avg_pace="8:15"
            )
            
            analysis = PerformanceAnalysis(
                metrics=metrics,
                strengths=[
                    "Consistent weekly mileage",
                    "Good pace progression",
                    "Strong endurance base"
                ],
                recommendations=[
                    "Add speed work sessions",
                    "Increase long run distance",
                    "Focus on recovery runs"
                ],
                analysis_date="2024-01-15"
            )
            
            logger.info(f"Performance analysis completed for {len(activities_data)} activities")
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            raise