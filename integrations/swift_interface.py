import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SwiftAppInterface:
    """Interface for communicating with your Swift Runaway app"""
    
    def __init__(self):
        self.base_url = settings.SWIFT_APP_BASE_URL
        self.api_key = settings.SWIFT_APP_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    async def notify_analysis_complete(
        self, 
        user_id: int, 
        analysis_summary: str,
        insights: Dict[str, Any]
    ) -> bool:
        """Notify Swift app that analysis is complete"""
        try:
            response = await self.client.post(
                "/api/analysis/notification",
                json={
                    "user_id": user_id,
                    "analysis_summary": analysis_summary,
                    "insights": insights,
                    "timestamp": datetime.now().isoformat()
                }
            )
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to notify Swift app: {str(e)}")
            return False
    
    async def update_training_recommendations(
        self,
        user_id: int,
        recommendations: List[Dict[str, Any]]
    ) -> bool:
        """Send training recommendations to Swift app"""
        try:
            response = await self.client.post(
                "/api/training/recommendations",
                json={
                    "user_id": user_id,
                    "recommendations": recommendations,
                    "timestamp": datetime.now().isoformat()
                }
            )
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to send recommendations to Swift app: {str(e)}")
            return False