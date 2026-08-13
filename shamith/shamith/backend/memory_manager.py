"""
Memory Manager – Conversation History
======================================
Manages chat history in Streamlit session state with a sliding
window to prevent token overflow. Automatically injects project
context into conversations.
"""

import streamlit as st
from datetime import datetime
from backend.config import Config


class MemoryManager:
    """Manages conversation memory for the AI chat assistant."""

    SESSION_KEY = "chat_history"

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._ensure_session()

    def _ensure_session(self):
        """Ensure the chat history key exists in session state."""
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = []

    # ── Message Management ───────────────────────────────────────────

    def add_message(self, role: str, content: str):
        """
        Append a message to the conversation history.

        Args:
            role: 'user', 'assistant', or 'system'.
            content: The message content.
        """
        self._ensure_session()
        st.session_state[self.SESSION_KEY].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })
        # Enforce sliding window
        max_msgs = self.config.MAX_CONVERSATION_MESSAGES
        if len(st.session_state[self.SESSION_KEY]) > max_msgs:
            # Keep the system message (if first) + last N messages
            history = st.session_state[self.SESSION_KEY]
            if history and history[0].get("role") == "system":
                st.session_state[self.SESSION_KEY] = [history[0]] + history[-(max_msgs - 1):]
            else:
                st.session_state[self.SESSION_KEY] = history[-max_msgs:]

    def get_history(self) -> list:
        """Return the full conversation history."""
        self._ensure_session()
        return st.session_state[self.SESSION_KEY]

    def get_messages_for_api(self, system_prompt: str = "", project_context: str = "") -> list:
        """
        Format conversation history for the Ollama API.

        Returns a list of dicts with 'role' and 'content' keys,
        prepended with the system prompt and project context.
        """
        self._ensure_session()
        messages = []

        # Add system prompt
        if system_prompt:
            context_addition = ""
            if project_context:
                context_addition = f"\n\n[CURRENT PROJECT CONTEXT]\n{project_context}"
            messages.append({
                "role": "system",
                "content": system_prompt + context_addition,
            })

        # Add conversation history (only role + content for API)
        for msg in st.session_state[self.SESSION_KEY]:
            if msg["role"] in ("user", "assistant"):
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        return messages

    def clear(self):
        """Reset the conversation history."""
        st.session_state[self.SESSION_KEY] = []

    def get_message_count(self) -> int:
        """Return the number of messages in history."""
        self._ensure_session()
        return len(st.session_state[self.SESSION_KEY])

    # ── Export ────────────────────────────────────────────────────────

    def export_chat(self) -> str:
        """
        Export the conversation as a formatted text string.

        Returns:
            Formatted chat transcript.
        """
        self._ensure_session()
        lines = [
            "=" * 60,
            "Agentic AI for Safety Monitoring with Construction Risk Analytics – Chat Export",
            f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
        ]

        for msg in st.session_state[self.SESSION_KEY]:
            role = msg["role"].upper()
            timestamp = msg.get("timestamp", "")
            content = msg["content"]
            lines.append(f"[{timestamp}] {role}:")
            lines.append(content)
            lines.append("-" * 40)
            lines.append("")

        return "\n".join(lines)
