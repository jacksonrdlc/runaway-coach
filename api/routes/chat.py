from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time
import logging
import uuid
from datetime import datetime
from supabase import create_client, Client

from models import ChatRequest, ChatResponse, ChatMessage
from core.agents.chat_agent import ChatAgent
from utils.config import get_settings

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Import auth from main module
from ..main import get_current_user, get_supervisor

# Initialize settings and Supabase
settings = get_settings()
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

# Lazy-initialize chat agent
_chat_agent: ChatAgent = None

def get_chat_agent() -> ChatAgent:
    """Get or create ChatAgent singleton"""
    global _chat_agent
    if _chat_agent is None:
        _chat_agent = ChatAgent()
        logger.info("ChatAgent initialized")
    return _chat_agent


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a chat message to the running coach AI.

    The agent will respond conversationally and may invoke analysis workflows
    when the user requests detailed analysis, training plans, or goal assessments.
    """
    start_time = time.time()
    user_id = current_user.get("sub")  # JWT subject contains user_id

    try:
        logger.info(f"Processing chat message from user: {user_id}")

        # Get or create conversation
        conversation_id = request.conversation_id
        conversation_history = []

        if conversation_id:
            # Load existing conversation
            logger.info(f"Loading conversation: {conversation_id}")
            result = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user_id).execute()

            if result.data and len(result.data) > 0:
                conversation = result.data[0]
                # Parse messages from JSONB
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in conversation.get("messages", [])
                ]
            else:
                logger.warning(f"Conversation {conversation_id} not found, creating new one")
                conversation_id = None

        # Create new conversation if needed
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            logger.info(f"Creating new conversation: {conversation_id}")

        # Process message with chat agent
        chat_agent = get_chat_agent()
        response_text, analysis_intent = await chat_agent.process_message(
            message=request.message,
            conversation_history=conversation_history,
            context=request.context
        )

        # Add new messages to history
        new_messages = conversation_history + [
            {"role": "user", "content": request.message, "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": response_text, "timestamp": datetime.utcnow().isoformat()}
        ]

        # Save conversation to Supabase
        conversation_data = {
            "id": conversation_id,
            "user_id": user_id,
            "messages": new_messages,
            "context": request.context,
            "updated_at": datetime.utcnow().isoformat()
        }

        # Upsert conversation
        supabase.table("conversations").upsert(conversation_data).execute()
        logger.info(f"Conversation saved: {conversation_id}")

        # Invoke analysis workflow if needed
        triggered_analysis = None
        if analysis_intent and request.context:
            logger.info(f"Analysis intent detected: {analysis_intent}")
            triggered_analysis = await _invoke_analysis_workflow(
                analysis_intent,
                request.context,
                user_id
            )

        processing_time = time.time() - start_time

        return ChatResponse(
            success=True,
            message=response_text,
            conversation_id=conversation_id,
            triggered_analysis=triggered_analysis,
            processing_time=processing_time
        )

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Chat message processing failed: {str(e)}", exc_info=True)

        return ChatResponse(
            success=False,
            message="I'm having trouble processing your message right now. Please try again.",
            conversation_id=conversation_id or str(uuid.uuid4()),
            error_message=str(e),
            processing_time=processing_time
        )


@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve a conversation by ID"""
    user_id = current_user.get("sub")

    try:
        result = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user_id).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {
            "success": True,
            "conversation": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """List recent conversations for the current user"""
    user_id = current_user.get("sub")

    try:
        result = supabase.table("conversations") \
            .select("id, created_at, updated_at") \
            .eq("user_id", user_id) \
            .order("updated_at", desc=True) \
            .limit(limit) \
            .execute()

        return {
            "success": True,
            "conversations": result.data
        }

    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    user_id = current_user.get("sub")

    try:
        result = supabase.table("conversations") \
            .delete() \
            .eq("id", conversation_id) \
            .eq("user_id", user_id) \
            .execute()

        return {
            "success": True,
            "message": "Conversation deleted"
        }

    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _invoke_analysis_workflow(
    analysis_type: str,
    context: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Invoke appropriate analysis workflow based on detected intent.

    Args:
        analysis_type: 'performance', 'goal', or 'plan'
        context: User context with activities, goals, profile
        user_id: User ID

    Returns:
        Analysis results dict
    """
    try:
        supervisor = get_supervisor()

        if analysis_type == "performance":
            # Run performance analysis
            runner_data = {
                "user_id": user_id,
                "activities": context.get("activities", []),
                "profile": context.get("profile", {}),
                "goals": context.get("goals", [])
            }
            analysis = await supervisor.analyze_runner(runner_data)
            return {
                "type": "performance",
                "data": analysis
            }

        elif analysis_type == "goal":
            # Run goal assessment
            from core.agents.goal_strategy_agent import GoalStrategyAgent
            goal_agent = GoalStrategyAgent()
            assessment = await goal_agent.assess_goal(
                context.get("goal", {}),
                context.get("activities", []),
                context.get("profile", {})
            )
            return {
                "type": "goal",
                "data": assessment
            }

        elif analysis_type == "plan":
            # Run workout planning
            from core.agents.workout_planning_agent import WorkoutPlanningAgent
            workout_agent = WorkoutPlanningAgent()
            plan = await workout_agent.create_plan(
                context.get("profile", {}),
                context.get("goal", {}),
                context.get("activities", [])
            )
            return {
                "type": "plan",
                "data": plan
            }

        return None

    except Exception as e:
        logger.error(f"Error invoking {analysis_type} workflow: {str(e)}")
        return {
            "type": analysis_type,
            "error": str(e)
        }
