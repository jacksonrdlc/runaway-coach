from typing import Dict, Any, List, Optional, Tuple
import logging
import os
import json
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatAgent:
    """
    Intelligent chat agent for running coaching conversations.
    Uses Claude for natural conversation and can invoke analysis workflows when needed.
    """

    def __init__(self):
        # Load .env file explicitly
        logger.info("Loading .env file for ChatAgent...")
        load_dotenv()

        # Initialize Anthropic client
        self.client = None
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = AsyncAnthropic(api_key=api_key)
                logger.info("ChatAgent: Anthropic client initialized successfully")
            else:
                logger.warning("ChatAgent: ANTHROPIC_API_KEY not found")
        except Exception as e:
            logger.error(f"ChatAgent: Client initialization failed: {e}")

    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt for the chat agent with optional context"""
        base_prompt = """You are an expert running coach AI assistant. You provide personalized advice, answer questions about running, training, pacing, and goals.

Your capabilities:
- Answer questions about running, training plans, pacing, recovery
- Provide encouragement and motivation
- Explain running concepts (easy runs, tempo, intervals, long runs)
- Interpret workout data and provide insights
- When users ask for detailed analysis, signal that you can run comprehensive analysis

Guidelines:
- Be encouraging and supportive
- Use miles for distances (not kilometers)
- Format paces as MM:SS (e.g., "8:15/mile")
- Keep responses conversational and concise
- If asked to analyze recent performance or create training plans, mention you can run detailed analysis

When to suggest analysis:
- User asks "analyze my training" or "how am I doing"
- User asks for a training plan
- User wants goal assessment
- User asks about pace zones or workout recommendations
"""

        # Add context if available
        if context:
            context_str = "\n\nCurrent Context:\n"
            if context.get("recent_activity"):
                activity = context["recent_activity"]
                context_str += f"- Latest run: {activity.get('distance', 0):.2f} miles at {activity.get('avg_pace', 'N/A')} pace\n"
            if context.get("weekly_mileage"):
                context_str += f"- Weekly mileage: {context['weekly_mileage']:.1f} miles\n"
            if context.get("goal"):
                context_str += f"- Current goal: {context['goal']}\n"

            base_prompt += context_str

        return base_prompt

    def _detect_analysis_intent(self, message: str) -> Optional[str]:
        """
        Detect if user message requires invoking analysis workflow.
        Returns analysis type if detected: 'performance', 'goal', 'plan', or None
        """
        message_lower = message.lower()

        # Performance analysis triggers
        if any(phrase in message_lower for phrase in [
            "analyze my", "how am i doing", "my progress", "my performance",
            "recent training", "last week", "past month"
        ]):
            return "performance"

        # Goal assessment triggers
        if any(phrase in message_lower for phrase in [
            "goal", "race plan", "can i run", "ready for"
        ]):
            return "goal"

        # Training plan triggers
        if any(phrase in message_lower for phrase in [
            "training plan", "workout plan", "what should i run",
            "create a plan", "build a plan"
        ]):
            return "plan"

        return None

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Process a chat message and return response.

        Args:
            message: User's message
            conversation_history: List of prior messages [{"role": "user|assistant", "content": "..."}]
            context: Optional context (recent activities, goals, profile)

        Returns:
            Tuple of (response_message, analysis_type)
            analysis_type is None for normal chat, or 'performance'/'goal'/'plan' if workflow should be invoked
        """

        # Detect if this requires analysis workflow
        analysis_intent = self._detect_analysis_intent(message)

        # If no Claude client, use fallback
        if not self.client:
            return self._get_fallback_response(message, analysis_intent), analysis_intent

        try:
            # Build messages for Claude
            system_prompt = self._build_system_prompt(context)

            # Combine conversation history with new message
            messages = conversation_history + [{"role": "user", "content": message}]

            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )

            # Extract response text
            response_text = response.content[0].text

            logger.info(f"ChatAgent: Generated response ({len(response_text)} chars)")
            return response_text, analysis_intent

        except Exception as e:
            logger.error(f"ChatAgent: Error processing message: {e}")
            return self._get_fallback_response(message, analysis_intent), analysis_intent

    def _get_fallback_response(self, message: str, analysis_intent: Optional[str]) -> str:
        """Fallback response when Claude API is unavailable"""

        if analysis_intent == "performance":
            return "I can analyze your recent performance, but I need my AI capabilities to be fully operational. Please check your API configuration."

        if analysis_intent == "goal":
            return "I can help assess your goals and create a race plan, but I need my AI capabilities to be fully operational. Please check your API configuration."

        if analysis_intent == "plan":
            return "I can create a personalized training plan for you, but I need my AI capabilities to be fully operational. Please check your API configuration."

        # Generic fallback
        return "I'm your running coach AI, but I'm currently operating in limited mode. Please ensure your API configuration is correct to unlock my full capabilities."

    async def get_quick_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Quick response without conversation history.
        Useful for one-off questions or when starting new conversation.
        """
        response, _ = await self.process_message(message, [], context)
        return response
