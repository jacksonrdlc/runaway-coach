from typing import Dict, Any, List, TypedDict
import logging
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage

from ..agents.performance_agent import PerformanceAnalysisAgent
from ..agents.goal_strategy_agent import GoalStrategyAgent
from ..agents.pace_optimization_agent import PaceOptimizationAgent
from ..agents.workout_planning_agent import WorkoutPlanningAgent

logger = logging.getLogger(__name__)

class RunnerAnalysisState(TypedDict):
    """State for the runner analysis workflow"""
    user_id: str
    activities: List[Dict[str, Any]]
    goals: List[Dict[str, Any]]
    profile: Dict[str, Any]
    
    # Analysis results
    performance_analysis: Dict[str, Any]
    goal_assessment: Dict[str, Any]
    pace_optimization: Dict[str, Any]
    workout_recommendations: List[Dict[str, Any]]
    
    # Final output
    final_analysis: Dict[str, Any]
    
    # Workflow metadata
    current_step: str
    completed_steps: List[str]
    processing_times: Dict[str, float]

class RunnerAnalysisWorkflow:
    def __init__(self):
        self.performance_agent = PerformanceAnalysisAgent()
        self.goal_agent = GoalStrategyAgent()
        self.pace_agent = PaceOptimizationAgent()
        self.workout_agent = WorkoutPlanningAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("RunnerAnalysisWorkflow initialized with LangGraph")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(RunnerAnalysisState)
        
        # Add nodes for each analysis step
        workflow.add_node("performance_analysis", self._performance_analysis_node)
        workflow.add_node("goal_assessment", self._goal_assessment_node)
        workflow.add_node("pace_optimization", self._pace_optimization_node)
        workflow.add_node("workout_planning", self._workout_planning_node)
        workflow.add_node("final_synthesis", self._final_synthesis_node)
        
        # Define the workflow edges
        workflow.set_entry_point("performance_analysis")
        workflow.add_edge("performance_analysis", "goal_assessment")
        workflow.add_edge("goal_assessment", "pace_optimization")
        workflow.add_edge("pace_optimization", "workout_planning")
        workflow.add_edge("workout_planning", "final_synthesis")
        workflow.add_edge("final_synthesis", END)
        
        return workflow
    
    async def _performance_analysis_node(self, state: RunnerAnalysisState) -> RunnerAnalysisState:
        """Node for performance analysis"""
        import time
        start_time = time.time()
        
        logger.info("Starting performance analysis node")
        
        try:
            analysis = await self.performance_agent.analyze_performance(state["activities"])
            
            state["performance_analysis"] = {
                "metrics": {
                    "weekly_mileage": analysis.metrics.weekly_mileage,
                    "recent_trend": analysis.metrics.recent_trend.value,
                    "consistency": analysis.metrics.consistency,
                    "avg_pace": analysis.metrics.avg_pace
                },
                "strengths": analysis.strengths,
                "recommendations": analysis.recommendations,
                "analysis_date": analysis.analysis_date
            }
            
            state["current_step"] = "performance_analysis"
            state["completed_steps"] = state.get("completed_steps", []) + ["performance_analysis"]
            state["processing_times"]["performance_analysis"] = time.time() - start_time
            
            logger.info("Performance analysis completed")
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            state["performance_analysis"] = {"error": str(e)}
        
        return state
    
    async def _goal_assessment_node(self, state: RunnerAnalysisState) -> RunnerAnalysisState:
        """Node for goal assessment"""
        import time
        start_time = time.time()
        
        logger.info("Starting goal assessment node")
        
        try:
            assessments = await self.goal_agent.assess_goals(state["goals"], state["activities"])
            
            state["goal_assessment"] = {
                "assessments": [
                    {
                        "goal_id": assessment.goal_id,
                        "goal_type": assessment.goal_type.value,
                        "current_status": assessment.current_status.value,
                        "progress_percentage": assessment.progress_percentage,
                        "feasibility_score": assessment.feasibility_score,
                        "recommendations": assessment.recommendations,
                        "timeline_adjustments": assessment.timeline_adjustments,
                        "key_metrics": assessment.key_metrics
                    }
                    for assessment in assessments
                ]
            }
            
            state["current_step"] = "goal_assessment"
            state["completed_steps"].append("goal_assessment")
            state["processing_times"]["goal_assessment"] = time.time() - start_time
            
            logger.info("Goal assessment completed")
            
        except Exception as e:
            logger.error(f"Goal assessment failed: {e}")
            state["goal_assessment"] = {"error": str(e)}
        
        return state
    
    async def _pace_optimization_node(self, state: RunnerAnalysisState) -> RunnerAnalysisState:
        """Node for pace optimization"""
        import time
        start_time = time.time()
        
        logger.info("Starting pace optimization node")
        
        try:
            optimization = await self.pace_agent.optimize_paces(state["activities"])
            
            state["pace_optimization"] = {
                "current_fitness_level": optimization.current_fitness_level,
                "recommended_paces": [
                    {
                        "pace_type": pace.pace_type.value,
                        "target_pace": pace.target_pace,
                        "pace_range": pace.pace_range,
                        "description": pace.description,
                        "heart_rate_zone": pace.heart_rate_zone
                    }
                    for pace in optimization.recommended_paces
                ],
                "weekly_pace_distribution": optimization.weekly_pace_distribution,
                "improvement_targets": optimization.improvement_targets
            }
            
            state["current_step"] = "pace_optimization"
            state["completed_steps"].append("pace_optimization")
            state["processing_times"]["pace_optimization"] = time.time() - start_time
            
            logger.info("Pace optimization completed")
            
        except Exception as e:
            logger.error(f"Pace optimization failed: {e}")
            state["pace_optimization"] = {"error": str(e)}
        
        return state
    
    async def _workout_planning_node(self, state: RunnerAnalysisState) -> RunnerAnalysisState:
        """Node for workout planning"""
        import time
        start_time = time.time()
        
        logger.info("Starting workout planning node")
        
        try:
            # Use the first goal for workout planning
            goal_data = state["goals"][0] if state["goals"] else {}
            workouts = await self.workout_agent.plan_workouts(
                state["activities"], 
                goal_data, 
                workout_count=3
            )
            
            state["workout_recommendations"] = [
                {
                    "workout_type": workout.workout_type.value,
                    "duration_minutes": workout.duration_minutes,
                    "distance_km": workout.distance_km,
                    "target_pace": workout.target_pace,
                    "description": workout.description,
                    "scheduled_date": workout.scheduled_date.isoformat(),
                    "run_number": workout.run_number
                }
                for workout in workouts
            ]
            
            state["current_step"] = "workout_planning"
            state["completed_steps"].append("workout_planning")
            state["processing_times"]["workout_planning"] = time.time() - start_time
            
            logger.info("Workout planning completed")
            
        except Exception as e:
            logger.error(f"Workout planning failed: {e}")
            state["workout_recommendations"] = [{"error": str(e)}]
        
        return state
    
    async def _final_synthesis_node(self, state: RunnerAnalysisState) -> RunnerAnalysisState:
        """Node for final synthesis of all analyses"""
        import time
        start_time = time.time()
        
        logger.info("Starting final synthesis node")
        
        # Combine all analysis results
        state["final_analysis"] = {
            "user_id": state["user_id"],
            "performance_metrics": state.get("performance_analysis", {}).get("metrics", {}),
            "goal_assessments": state.get("goal_assessment", {}).get("assessments", []),
            "pace_recommendations": state.get("pace_optimization", {}).get("recommended_paces", []),
            "workout_plan": state.get("workout_recommendations", []),
            "summary_recommendations": self._generate_summary_recommendations(state),
            "workflow_metadata": {
                "completed_steps": state["completed_steps"],
                "processing_times": state["processing_times"],
                "total_processing_time": sum(state["processing_times"].values()),
                "workflow_version": "1.0"
            }
        }
        
        state["current_step"] = "completed"
        state["completed_steps"].append("final_synthesis")
        state["processing_times"]["final_synthesis"] = time.time() - start_time
        
        logger.info("Final synthesis completed")
        
        return state
    
    def _generate_summary_recommendations(self, state: RunnerAnalysisState) -> List[str]:
        """Generate high-level recommendations based on all analyses"""
        recommendations = []
        
        # Performance-based recommendations
        if state.get("performance_analysis", {}).get("recommendations"):
            recommendations.extend(state["performance_analysis"]["recommendations"][:2])
        
        # Goal-based recommendations
        goal_recs = []
        for assessment in state.get("goal_assessment", {}).get("assessments", []):
            goal_recs.extend(assessment.get("recommendations", [])[:1])
        recommendations.extend(goal_recs[:2])
        
        # Pace-based recommendations
        if state.get("pace_optimization", {}).get("improvement_targets"):
            recommendations.extend(state["pace_optimization"]["improvement_targets"][:1])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def analyze_runner(self, runner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete analysis workflow"""
        
        # Initialize state
        initial_state = RunnerAnalysisState(
            user_id=runner_data.get("user_id", "unknown"),
            activities=runner_data.get("activities", []),
            goals=runner_data.get("goals", []),
            profile=runner_data.get("profile", {}),
            performance_analysis={},
            goal_assessment={},
            pace_optimization={},
            workout_recommendations=[],
            final_analysis={},
            current_step="initializing",
            completed_steps=[],
            processing_times={}
        )
        
        # Execute the workflow
        logger.info(f"Starting LangGraph workflow for user: {initial_state['user_id']}")
        
        final_state = await self.app.ainvoke(initial_state)
        
        logger.info(f"LangGraph workflow completed for user: {initial_state['user_id']}")
        
        return final_state["final_analysis"]
    
    def get_workflow_graph(self) -> str:
        """Get the workflow graph as Mermaid diagram"""
        try:
            return self.workflow.get_graph().draw_mermaid()
        except Exception as e:
            logger.error(f"Failed to generate graph: {e}")
            return f"Error generating graph: {str(e)}"
    
    def get_workflow_state_schema(self) -> Dict[str, Any]:
        """Get the workflow state schema"""
        return {
            "user_id": "string",
            "activities": "List[Dict]",
            "goals": "List[Dict]", 
            "profile": "Dict",
            "performance_analysis": "Dict",
            "goal_assessment": "Dict",
            "pace_optimization": "Dict",
            "workout_recommendations": "List[Dict]",
            "final_analysis": "Dict",
            "current_step": "string",
            "completed_steps": "List[string]",
            "processing_times": "Dict[string, float]"
        }