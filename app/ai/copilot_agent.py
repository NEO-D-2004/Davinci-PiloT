"""
AI Copilot Agent for DaVinci PiloT Milestone 6.
Maintains multi-turn conversational context and routes queries through NVIDIA NIM GLM-5.2 Master Agent.
Automatically injects live DaVinci Resolve project context into every system prompt turn.
"""

from typing import List, Dict, Any, Optional
from app.ai.nim_client import nim_client
from app.services.logger_service import app_logger


class CopilotAgent:
    """
    GLM-5.2 powered AI Copilot with persistent multi-turn conversation history.
    Injects live DaVinci Resolve context (project, timeline, clips) into every API call.
    """

    MAX_HISTORY_TURNS = 10  # Keep last 10 user+assistant pairs in context

    def __init__(self) -> None:
        self.nim = nim_client
        self.conversation_history: List[Dict[str, str]] = []
        self._resolve_context: str = ""

    def update_resolve_context(
        self,
        project_name: str = "",
        timeline_name: str = "",
        clip_count: int = 0,
        media_asset_count: int = 0,
        last_analysis_summary: str = ""
    ) -> None:
        """Update stored Resolve context used in every chat turn."""
        ctx_parts = [f"Active DaVinci Resolve Project: '{project_name}'" if project_name else "No active DaVinci Resolve project."]
        if timeline_name:
            ctx_parts.append(f"Active Timeline: '{timeline_name}' with {clip_count} clips.")
        if media_asset_count > 0:
            ctx_parts.append(f"Media Pool: {media_asset_count} assets available.")
        if last_analysis_summary:
            ctx_parts.append(f"Last AI Analysis: {last_analysis_summary}")
        self._resolve_context = "\n".join(ctx_parts)
        app_logger.debug(f"CopilotAgent resolve context updated: {project_name}/{timeline_name}")

    def build_system_prompt(self) -> str:
        """Construct the full system prompt with current DaVinci Resolve context."""
        base_prompt = (
            "You are the DaVinci PiloT AI Copilot — an expert video editing assistant "
            "powered by the GLM-5.2 Master Agent. You have full awareness of the user's "
            "active DaVinci Resolve project and can help with editing decisions, timeline "
            "optimization, smart cut suggestions, color grading advice, audio cleanup, "
            "and professional workflow recommendations.\n\n"
            "Always be concise, actionable, and professional. Format lists with bullet points. "
            "If asked to perform an action in Resolve, describe the exact steps clearly."
        )
        if self._resolve_context:
            base_prompt += f"\n\n## Current Resolve Context:\n{self._resolve_context}"
        return base_prompt

    def send_message(self, user_text: str) -> str:
        """
        Send a user message to GLM-5.2 via NVIDIA NIM and return the AI response text.
        Maintains full multi-turn conversation history for context-aware responses.
        """
        user_text = user_text.strip()
        if not user_text:
            return ""

        # Build messages: system + truncated history + current user message
        messages = [{"role": "system", "content": self.build_system_prompt()}]

        # Add conversation history (last N turns)
        history_slice = self.conversation_history[-self.MAX_HISTORY_TURNS * 2:]
        messages.extend(history_slice)

        # Add current user message
        messages.append({"role": "user", "content": user_text})

        app_logger.info(f"CopilotAgent sending message to GLM-5.2 (history: {len(history_slice)} messages)")

        # Call NVIDIA NIM Master Agent
        response = self.nim.query_master_agent(
            prompt="\n".join(
                f"[{m['role'].upper()}] {m['content']}"
                for m in messages
                if m["role"] != "system"
            )
        )

        ai_content = response.get("content", "").strip()

        if not ai_content:
            # Graceful fallback if API call fails
            status = response.get("error", "Unknown error")
            app_logger.warning(f"CopilotAgent got empty response: {status}")
            if "timeout" in str(status).lower():
                ai_content = (
                    "⚠️ The NVIDIA NIM API timed out. Please check your internet connection "
                    "and try again. Your API key is configured correctly."
                )
            else:
                ai_content = (
                    f"⚠️ NVIDIA NIM API returned an error: {status}\n\n"
                    "Please verify your API key in Settings → AI Provider."
                )

        # Store turn in history
        self.conversation_history.append({"role": "user", "content": user_text})
        self.conversation_history.append({"role": "assistant", "content": ai_content})

        app_logger.info(f"CopilotAgent response received ({len(ai_content)} chars)")
        return ai_content

    def clear_history(self) -> None:
        """Reset conversation history for a fresh session."""
        self.conversation_history.clear()
        app_logger.info("CopilotAgent conversation history cleared.")

    def get_history_count(self) -> int:
        """Return number of stored conversation turns (user + assistant pairs)."""
        return len(self.conversation_history) // 2

    def get_quick_commands(self) -> List[Dict[str, str]]:
        """Return predefined quick command chips shown in the UI."""
        return [
            {"label": "📋 Summarize my timeline", "prompt": "Give me a summary of my current timeline, including clip count, total duration, and any editing recommendations."},
            {"label": "✂️ Find best cuts", "prompt": "Based on my timeline clips, where would you suggest making smart cuts to improve pacing and flow?"},
            {"label": "🔇 Remove all silence", "prompt": "Identify all long silence gaps in my timeline and tell me how to efficiently ripple-cut them in DaVinci Resolve."},
            {"label": "⚠️ Clips needing attention", "prompt": "Which of my current timeline clips might need color correction, audio cleanup, or trimming? Give me a prioritized list."},
            {"label": "🎬 Suggest edit structure", "prompt": "Based on my current media pool and timeline, suggest a professional edit structure with an intro, main sections, and outro."},
            {"label": "🎵 Audio recommendations", "prompt": "What are your audio mixing and cleanup recommendations for my current timeline?"},
        ]
