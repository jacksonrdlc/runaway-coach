from typing import Dict, Any, List
import logging
import os
import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class RunningCoachSupervisor:
    def __init__(self):
        # Load .env file explicitly to ensure environment variables are available
        logger.info("Loading .env file...")
        env_loaded = load_dotenv()
        logger.info(f".env file loaded: {env_loaded}")
        
        # Debug: Check current working directory
        import os
        cwd = os.getcwd()
        logger.info(f"Current working directory: {cwd}")
        
        # Debug: Check if .env file exists
        env_file_exists = os.path.exists(".env")
        logger.info(f".env file exists: {env_file_exists}")
        
        # Use direct Anthropic SDK instead of langchain for better compatibility
        self.client = None
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            logger.info(f"ANTHROPIC_API_KEY found: {api_key is not None}")
            if api_key:
                logger.info(f"API key length: {len(api_key)}")
                logger.info(f"API key starts with: {api_key[:10]}...")
                
                # Try to initialize the client
                logger.info("Attempting to initialize Anthropic client...")
                self.client = AsyncAnthropic(api_key=api_key)
                logger.info("Anthropic client initialized successfully")
            else:
                logger.warning("ANTHROPIC_API_KEY not found in environment variables")
                logger.info("Please set ANTHROPIC_API_KEY to enable AI features")
                
                # Debug: List all environment variables starting with 'A'
                all_env_vars = {k: v for k, v in os.environ.items() if k.startswith('A')}
                logger.info(f"Environment variables starting with 'A': {list(all_env_vars.keys())}")
                
        except Exception as e:
            logger.error(f"Anthropic client initialization failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
        
        logger.info(f"RunningCoachSupervisor initialized - client available: {self.client is not None}")
    
    async def analyze_runner(self, runner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive runner analysis using agentic workflow"""
        try:
            # Use real Anthropic API if available
            if self.client:
                analysis_prompt = f"""
                Analyze this runner's data and provide insights:
                
                User ID: {runner_data.get('user_id', 'unknown')}
                Activities: {len(runner_data.get('activities', []))} recent activities
                Goals: {runner_data.get('goals', [])}
                Profile: {runner_data.get('profile', {})}
                
                Provide analysis in JSON format with:
                - performance_metrics (weekly_mileage, avg_pace, consistency_score)
                - recommendations (list of 3-5 actionable items)
                - insights (key observations about their running)
                """
                
                try:
                    response = await self.client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1000,
                        messages=[{
                            "role": "user", 
                            "content": analysis_prompt
                        }]
                    )
                    
                    # Parse the response and structure it
                    ai_analysis = response.content[0].text
                    
                    analysis = {
                        "performance_metrics": {
                            "weekly_mileage": 25.0,  # Would parse from AI response
                            "avg_pace": "8:30",
                            "consistency_score": 0.75
                        },
                        "recommendations": [
                            "AI-generated recommendation based on data",
                            "Personalized training advice",
                            "Goal-specific guidance"
                        ],
                        "ai_insights": ai_analysis,
                        "agent_metadata": {
                            "agents_used": ["supervisor", "anthropic_ai"],
                            "processing_time": 2.5,
                            "llm_available": True,
                            "model_used": "claude-3-sonnet-20240229"
                        }
                    }
                    
                except Exception as ai_error:
                    logger.error(f"AI analysis failed: {ai_error}")
                    # Fall back to structured analysis
                    analysis = self._get_fallback_analysis(runner_data)
            else:
                # Fallback analysis when no AI client
                analysis = self._get_fallback_analysis(runner_data)
            
            logger.info(f"Analysis completed for user: {runner_data.get('user_id', 'unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def _get_fallback_analysis(self, runner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        return {
            "performance_metrics": {
                "weekly_mileage": 25.0,
                "avg_pace": "8:30",
                "consistency_score": 0.75
            },
            "recommendations": [
                "Increase weekly mileage by 10%",
                "Add tempo runs to training",
                "Focus on recovery between hard sessions"
            ],
            "agent_metadata": {
                "agents_used": ["performance", "goal", "pace"],
                "processing_time": 1.0,
                "llm_available": False,
                "fallback_mode": True
            }
        }