"""
Conversation manager for tracking and persisting chat history.
Maintains a rolling window of messages and saves to disk.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default history file location
DEFAULT_HISTORY_FILE = Path.home() / ".ollama_agents" / "history.json"
# Maximum messages to keep in memory
DEFAULT_MAX_MESSAGES = 100
# Maximum messages to keep in rolling window
DEFAULT_WINDOW_SIZE = 20


class ConversationManager:
    """
    Manages conversation history with persistence.

    Features:
    - Rolling message window (last N messages)
    - Persistent storage to JSON file
    - Async operations with locks
    - Message metadata (timestamp, role, source)
    """

    def __init__(
        self,
        history_file: Optional[Path] = None,
        window_size: int = DEFAULT_WINDOW_SIZE,
        max_messages: int = DEFAULT_MAX_MESSAGES,
    ):
        """
        Initialize the conversation manager.

        Args:
            history_file: Path to save conversation history
            window_size: Number of messages to keep in active window
            max_messages: Maximum total messages before pruning
        """
        self.history_file = history_file or DEFAULT_HISTORY_FILE
        self.window_size = window_size
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

        # Ensure directory exists
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized ConversationManager (window_size={window_size}, "
            f"history_file={self.history_file})"
        )

    async def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a message to the conversation.

        Args:
            role: Role/source of message (user, assistant, agent, system)
            content: Message content
            metadata: Optional metadata dict (agent_name, task_id, etc.)

        Returns:
            Message dict with timestamp
        """
        async with self._lock:
            message = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                **(metadata or {}),
            }

            self.messages.append(message)

            # Enforce max_messages limit
            if len(self.messages) > self.max_messages:
                excess = len(self.messages) - self.max_messages
                self.messages = self.messages[excess:]
                logger.debug(
                    f"Pruned {excess} oldest messages (limit: {self.max_messages})"
                )

            # Save to disk
            await self._save_to_disk()

            logger.debug(f"Added message from {role}: {content[:50]}...")
            return message

    async def get_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            limit: Number of recent messages to return (None = all)

        Returns:
            List of message dicts
        """
        async with self._lock:
            if limit is None:
                return list(self.messages)
            else:
                return list(self.messages[-limit:])

    async def get_window(self) -> List[Dict[str, Any]]:
        """
        Get the current message window (last N messages).

        Returns:
            List of recent messages (up to window_size)
        """
        async with self._lock:
            return list(self.messages[-self.window_size :])

    async def clear(self) -> None:
        """Clear all conversation history."""
        async with self._lock:
            self.messages.clear()
            await self._save_to_disk()
            logger.info("Conversation history cleared")

    async def export(
        self,
        output_path: Optional[Path] = None,
        format: str = "json",
    ) -> Path:
        """
        Export conversation to file.

        Args:
            output_path: Path to save export (default: timestamped file)
            format: Export format (json or markdown)

        Returns:
            Path to exported file
        """
        async with self._lock:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = (
                    self.history_file.parent
                    / "exports"
                    / f"conversation_{timestamp}.{format}"
                )

            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format == "json":
                with open(output_path, "w") as f:
                    json.dump(self.messages, f, indent=2)
            elif format == "markdown":
                with open(output_path, "w") as f:
                    f.write("# Conversation Export\n\n")
                    f.write(
                        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    )
                    f.write(f"Total Messages: {len(self.messages)}\n\n")
                    f.write("---\n\n")

                    for msg in self.messages:
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        timestamp = msg.get("timestamp", "")

                        f.write(f"**{role}** ({timestamp[:19]})\n\n")
                        f.write(f"{content}\n\n")
                        f.write("---\n\n")
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported conversation to {output_path}")
            return output_path

    async def search(
        self, query: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search conversation history.

        Args:
            query: Search query (case-insensitive substring match)
            limit: Maximum results to return

        Returns:
            List of matching messages
        """
        async with self._lock:
            query_lower = query.lower()
            results = [
                msg
                for msg in self.messages
                if query_lower in msg.get("content", "").lower()
            ]

            if limit:
                results = results[-limit:]

            return results

    async def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about the conversation.

        Returns:
            Summary dict with message counts and metadata
        """
        async with self._lock:
            role_counts = {}
            for msg in self.messages:
                role = msg.get("role", "unknown")
                role_counts[role] = role_counts.get(role, 0) + 1

            return {
                "total_messages": len(self.messages),
                "by_role": role_counts,
                "oldest_message": (
                    self.messages[0].get("timestamp") if self.messages else None
                ),
                "newest_message": (
                    self.messages[-1].get("timestamp") if self.messages else None
                ),
            }

    async def _save_to_disk(self) -> None:
        """Save conversation history to disk (must be called with lock held)."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.history_file, "w") as f:
                json.dump(
                    {
                        "messages": self.messages,
                        "saved_at": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            logger.debug(f"Saved conversation to {self.history_file}")

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

    async def load_from_disk(self) -> int:
        """
        Load conversation history from disk.

        Returns:
            Number of messages loaded
        """
        async with self._lock:
            if not self.history_file.exists():
                logger.debug(f"History file not found: {self.history_file}")
                return 0

            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self.messages = data.get("messages", [])

                logger.info(
                    f"Loaded {len(self.messages)} messages from {self.history_file}"
                )
                return len(self.messages)

            except Exception as e:
                logger.error(f"Failed to load conversation: {e}")
                return 0

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about messages (non-async).

        Returns:
            Statistics dict
        """
        if not self.messages:
            return {
                "total": 0,
                "by_role": {},
                "avg_length": 0,
            }

        role_counts = {}
        total_length = 0

        for msg in self.messages:
            role = msg.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
            total_length += len(msg.get("content", ""))

        return {
            "total": len(self.messages),
            "by_role": role_counts,
            "avg_length": (
                total_length / len(self.messages) if self.messages else 0
            ),
        }
