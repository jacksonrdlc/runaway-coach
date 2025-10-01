"""
Enhanced Runner Analysis Workflow

LangGraph workflow using full Strava data model for comprehensive analysis.
"""

from typing import Dict, Any, List, TypedDict, Optional
import logging
from langgraph.graph import StateGraph, END
import time

from models.strava import Athlete, AthleteStats, EnhancedActivity, RunningGoal, Gear
from integrations.supabase_queries import SupabaseQueries
from ..agents.performance_agent import PerformanceAnalysisAgent
from ..agents.goal_strategy_agent import GoalStrategyAgent
from ..agents.workout_planning_agent import WorkoutPlanningAgent

logger = logging.getLogger(__name__)


class EnhancedRunnerAnalysisState(TypedDict):
    """Enhanced state for runner analysis workflow"""
    # Input data
    athlete_id: int
    athlete: Optional[Athlete]
    stats: Optional[AthleteStats]
    activities: List[EnhancedActivity]
    running_goals: List[RunningGoal]
    gear: List[Gear]

    # Analysis results
    performance_analysis: Dict[str, Any]
    goal_assessment: Dict[str, Any]
    workout_plan: List[Dict[str, Any]]
    gear_health: Dict[str, Any]
    commitment_tracking: Dict[str, Any]

    # Final output
    final_analysis: Dict[str, Any]

    # Workflow metadata
    current_step: str
    completed_steps: List[str]
    processing_times: Dict[str, float]
    errors: List[Dict[str, str]]


class EnhancedRunnerAnalysisWorkflow:
    """Enhanced workflow with full Strava data integration"""

    def __init__(self, supabase_queries: SupabaseQueries):
        self.supabase = supabase_queries

        # Initialize agents with Supabase integration
        self.performance_agent = PerformanceAnalysisAgent()
        self.goal_agent = GoalStrategyAgent(supabase_queries=supabase_queries)
        self.workout_agent = WorkoutPlanningAgent(supabase_queries=supabase_queries)

        # Build the workflow graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

        logger.info("EnhancedRunnerAnalysisWorkflow initialized")

    def _build_workflow(self) -> StateGraph:
        """Build the enhanced LangGraph workflow"""
        workflow = StateGraph(EnhancedRunnerAnalysisState)

        # Add nodes for each analysis step
        workflow.add_node("load_data", self._load_data_node)
        workflow.add_node("performance_analysis", self._performance_analysis_node)
        workflow.add_node("goal_assessment", self._goal_assessment_node)
        workflow.add_node("commitment_tracking", self._commitment_tracking_node)
        workflow.add_node("workout_planning", self._workout_planning_node)
        workflow.add_node("gear_analysis", self._gear_analysis_node)
        workflow.add_node("final_synthesis", self._final_synthesis_node)

        # Define the workflow edges
        workflow.set_entry_point("load_data")
        workflow.add_edge("load_data", "performance_analysis")
        workflow.add_edge("performance_analysis", "goal_assessment")
        workflow.add_edge("goal_assessment", "commitment_tracking")
        workflow.add_edge("commitment_tracking", "workout_planning")
        workflow.add_edge("workout_planning", "gear_analysis")
        workflow.add_edge("gear_analysis", "final_synthesis")
        workflow.add_edge("final_synthesis", END)

        return workflow

    async def _load_data_node(self, state: EnhancedRunnerAnalysisState) -> EnhancedRunnerAnalysisState:
        """Load all required data from Supabase"""
        start_time = time.time()
        logger.info(f"Loading data for athlete {state['athlete_id']}")

        try:
            athlete_id = state["athlete_id"]

            # Load athlete data
            athlete = await self.supabase.get_athlete_by_id(athlete_id)
            stats = await self.supabase.get_athlete_stats(athlete_id)
            activities = await self.supabase.get_recent_activities(athlete_id, limit=30)
            running_goals = await self.supabase.get_running_goals(athlete_id, active_only=True)
            gear = await self.supabase.get_athlete_gear(athlete_id)

            state["athlete"] = athlete
            state["stats"] = stats
            state["activities"] = activities
            state["running_goals"] = running_goals
            state["gear"] = gear

            state["current_step"] = "load_data"
            state["completed_steps"] = state.get("completed_steps", []) + ["load_data"]
            state["processing_times"] = state.get("processing_times", {})
            state["processing_times"]["load_data"] = time.time() - start_time
            state["errors"] = state.get("errors", [])

            logger.info(
                f"Data loaded: {len(activities)} activities, "
                f"{len(running_goals)} goals, {len(gear)} gear items"
            )

        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            state["errors"].append({"step": "load_data", "error": str(e)})

        return state

    async def _performance_analysis_node(
        self,
        state: EnhancedRunnerAnalysisState
    ) -> EnhancedRunnerAnalysisState:
        """Enhanced performance analysis node"""
        start_time = time.time()
        logger.info("Starting enhanced performance analysis")

        try:
            if not state.get("athlete") or not state.get("stats"):
                raise ValueError("Missing athlete or stats data")

            analysis = await self.performance_agent.analyze_performance_enhanced(
                athlete=state["athlete"],
                stats=state["stats"],
                activities=state["activities"]
            )

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
            state["completed_steps"].append("performance_analysis")
            state["processing_times"]["performance_analysis"] = time.time() - start_time

            logger.info("Enhanced performance analysis completed")

        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            state["errors"].append({"step": "performance_analysis", "error": str(e)})
            state["performance_analysis"] = {"error": str(e)}

        return state

    async def _goal_assessment_node(
        self,
        state: EnhancedRunnerAnalysisState
    ) -> EnhancedRunnerAnalysisState:
        """Enhanced goal assessment node"""
        start_time = time.time()
        logger.info("Starting enhanced goal assessment")

        try:
            assessments = await self.goal_agent.assess_running_goals_enhanced(
                state["athlete_id"]
            )

            state["goal_assessment"] = {
                "goal_count": len(assessments),
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

            logger.info(f"Goal assessment completed for {len(assessments)} goals")

        except Exception as e:
            logger.error(f"Goal assessment failed: {e}")
            state["errors"].append({"step": "goal_assessment", "error": str(e)})
            state["goal_assessment"] = {"error": str(e)}

        return state

    async def _commitment_tracking_node(
        self,
        state: EnhancedRunnerAnalysisState
    ) -> EnhancedRunnerAnalysisState:
        """Track daily commitments"""
        start_time = time.time()
        logger.info("Starting commitment tracking")

        try:
            tracking = await self.goal_agent.track_daily_commitments(state["athlete_id"])

            state["commitment_tracking"] = tracking

            state["current_step"] = "commitment_tracking"
            state["completed_steps"].append("commitment_tracking")
            state["processing_times"]["commitment_tracking"] = time.time() - start_time

            logger.info(
                f"Commitment tracking completed: "
                f"{tracking.get('current_streak', 0)} day streak"
            )

        except Exception as e:
            logger.error(f"Commitment tracking failed: {e}")
            state["errors"].append({"step": "commitment_tracking", "error": str(e)})
            state["commitment_tracking"] = {"error": str(e)}

        return state

    async def _workout_planning_node(
        self,
        state: EnhancedRunnerAnalysisState
    ) -> EnhancedRunnerAnalysisState:
        """Enhanced workout planning with gear and segments"""
        start_time = time.time()
        logger.info("Starting enhanced workout planning")

        try:
            # Use first active goal if available
            goal_id = None
            if state.get("running_goals"):
                goal_id = state["running_goals"][0].id

            workouts = await self.workout_agent.plan_workouts_enhanced(
                athlete_id=state["athlete_id"],
                goal_id=goal_id,
                days=7
            )

            state["workout_plan"] = [
                {
                    "run_number": workout.run_number,
                    "workout_type": workout.workout_type.value,
                    "scheduled_date": workout.scheduled_date.isoformat(),
                    "duration_minutes": workout.duration_minutes,
                    "distance_km": workout.distance_km,
                    "distance_miles": workout.distance_km * 0.621371,
                    "target_pace": workout.target_pace,
                    "description": workout.description,
                    "recommended_gear": {
                        "gear_id": workout.recommended_gear_id,
                        "gear_name": workout.recommended_gear_name
                    } if workout.recommended_gear_id else None,
                    "segment": {
                        "segment_id": workout.segment_id,
                        "segment_name": workout.segment_name
                    } if workout.segment_id else None
                }
                for workout in workouts
            ]

            state["current_step"] = "workout_planning"
            state["completed_steps"].append("workout_planning")
            state["processing_times"]["workout_planning"] = time.time() - start_time

            logger.info(f"Workout planning completed: {len(workouts)} workouts")

        except Exception as e:
            logger.error(f"Workout planning failed: {e}")
            state["errors"].append({"step": "workout_planning", "error": str(e)})
            state["workout_plan"] = []

        return state

    async def _gear_analysis_node(
        self,
        state: EnhancedRunnerAnalysisState
    ) -> EnhancedRunnerAnalysisState:
        """Analyze gear health"""
        start_time = time.time()
        logger.info("Starting gear health analysis")

        try:
            health_report = await self.workout_agent.analyze_gear_health(state["athlete_id"])

            state["gear_health"] = health_report

            state["current_step"] = "gear_analysis"
            state["completed_steps"].append("gear_analysis")
            state["processing_times"]["gear_analysis"] = time.time() - start_time

            logger.info(
                f"Gear analysis completed: {health_report.get('gear_count', 0)} items analyzed"
            )

        except Exception as e:
            logger.error(f"Gear analysis failed: {e}")
            state["errors"].append({"step": "gear_analysis", "error": str(e)})
            state["gear_health"] = {"error": str(e)}

        return state

    async def _final_synthesis_node(
        self,
        state: EnhancedRunnerAnalysisState
    ) -> EnhancedRunnerAnalysisState:
        """Synthesize all analyses into final report"""
        start_time = time.time()
        logger.info("Starting final synthesis")

        # Combine all analysis results
        state["final_analysis"] = {
            "athlete": {
                "id": state["athlete"].id if state.get("athlete") else None,
                "name": f"{state['athlete'].first_name} {state['athlete'].last_name}" if state.get("athlete") else None,
                "location": f"{state['athlete'].city}, {state['athlete'].state}" if state.get("athlete") else None
            },
            "stats": {
                "total_activities": state["stats"].count if state.get("stats") else 0,
                "total_distance_miles": (float(state["stats"].distance) / 1000) * 0.621371 if state.get("stats") else 0,
                "ytd_distance_miles": (float(state["stats"].ytd_distance) / 1000) * 0.621371 if state.get("stats") else 0,
                "total_elevation_gain_meters": float(state["stats"].elevation_gain) if state.get("stats") else 0,
                "achievement_count": state["stats"].achievement_count if state.get("stats") else 0
            } if state.get("stats") else {},
            "performance": state.get("performance_analysis", {}),
            "goals": state.get("goal_assessment", {}),
            "commitments": state.get("commitment_tracking", {}),
            "workouts": state.get("workout_plan", []),
            "gear_health": state.get("gear_health", {}),
            "summary_recommendations": self._generate_summary_recommendations(state),
            "workflow_metadata": {
                "completed_steps": state["completed_steps"],
                "processing_times": state["processing_times"],
                "total_processing_time": sum(state["processing_times"].values()),
                "errors": state.get("errors", []),
                "workflow_version": "2.0-enhanced"
            }
        }

        state["current_step"] = "completed"
        state["completed_steps"].append("final_synthesis")
        state["processing_times"]["final_synthesis"] = time.time() - start_time

        logger.info("Final synthesis completed")

        return state

    def _generate_summary_recommendations(self, state: EnhancedRunnerAnalysisState) -> List[str]:
        """Generate high-level summary recommendations"""
        recommendations = []

        # Performance recommendations
        perf_recs = state.get("performance_analysis", {}).get("recommendations", [])
        if perf_recs:
            recommendations.extend(perf_recs[:2])

        # Goal recommendations
        goal_data = state.get("goal_assessment", {})
        if goal_data.get("assessments"):
            for assessment in goal_data["assessments"][:2]:
                recs = assessment.get("recommendations", [])
                if recs:
                    recommendations.append(recs[0])

        # Commitment recommendations
        commitment_recs = state.get("commitment_tracking", {}).get("recommendations", [])
        if commitment_recs:
            recommendations.append(commitment_recs[0])

        # Gear recommendations
        gear_health = state.get("gear_health", {})
        if gear_health.get("needs_replacement"):
            gear_item = gear_health["needs_replacement"][0]
            recommendations.append(
                f"Replace {gear_item['gear_name']} - {gear_item['total_miles']:.0f} miles"
            )

        return recommendations[:5]  # Top 5 recommendations

    async def analyze_runner(self, athlete_id: int) -> Dict[str, Any]:
        """Run the complete enhanced analysis workflow"""

        # Initialize state
        initial_state = EnhancedRunnerAnalysisState(
            athlete_id=athlete_id,
            athlete=None,
            stats=None,
            activities=[],
            running_goals=[],
            gear=[],
            performance_analysis={},
            goal_assessment={},
            workout_plan=[],
            gear_health={},
            commitment_tracking={},
            final_analysis={},
            current_step="initializing",
            completed_steps=[],
            processing_times={},
            errors=[]
        )

        # Execute the workflow
        logger.info(f"Starting enhanced workflow for athlete: {athlete_id}")

        final_state = await self.app.ainvoke(initial_state)

        logger.info(f"Enhanced workflow completed for athlete: {athlete_id}")

        return final_state["final_analysis"]


# Export
__all__ = ["EnhancedRunnerAnalysisWorkflow", "EnhancedRunnerAnalysisState"]