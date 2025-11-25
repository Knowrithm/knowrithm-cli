"""Context management for the Knowrithm CLI.

Maintains active agent, conversation, and organization context to reduce
the need for repeatedly specifying IDs in commands.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .. import config

CONTEXT_FILE = config.CONFIG_DIR / "context.json"


class Context:
    """Manages CLI context (active agent, conversation, organization)."""

    def __init__(self) -> None:
        self.agent_id: Optional[str] = None
        self.agent_name: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self.conversation_title: Optional[str] = None
        self.organization_id: Optional[str] = None
        self.organization_name: Optional[str] = None
        self._load()

    def _load(self) -> None:
        """Load context from disk."""
        if CONTEXT_FILE.exists():
            try:
                with CONTEXT_FILE.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    self.agent_id = data.get("agent_id")
                    self.agent_name = data.get("agent_name")
                    self.conversation_id = data.get("conversation_id")
                    self.conversation_title = data.get("conversation_title")
                    self.organization_id = data.get("organization_id")
                    self.organization_name = data.get("organization_name")
            except (json.JSONDecodeError, IOError):
                pass  # Ignore corrupted context

    def _save(self) -> None:
        """Persist context to disk."""
        config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "conversation_id": self.conversation_id,
            "conversation_title": self.conversation_title,
            "organization_id": self.organization_id,
            "organization_name": self.organization_name,
        }
        with CONTEXT_FILE.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def set_agent(self, agent_id: str, agent_name: Optional[str] = None) -> None:
        """Set the active agent."""
        self.agent_id = agent_id
        self.agent_name = agent_name or agent_id
        self._save()

    def set_conversation(
        self, conversation_id: str, conversation_title: Optional[str] = None
    ) -> None:
        """Set the active conversation."""
        self.conversation_id = conversation_id
        self.conversation_title = conversation_title or conversation_id
        self._save()

    def set_organization(
        self, organization_id: str, organization_name: Optional[str] = None
    ) -> None:
        """Set the active organization."""
        self.organization_id = organization_id
        self.organization_name = organization_name or organization_id
        self._save()

    def clear_agent(self) -> None:
        """Clear the active agent."""
        self.agent_id = None
        self.agent_name = None
        self._save()

    def clear_conversation(self) -> None:
        """Clear the active conversation."""
        self.conversation_id = None
        self.conversation_title = None
        self._save()

    def clear_organization(self) -> None:
        """Clear the active organization."""
        self.organization_id = None
        self.organization_name = None
        self._save()

    def clear_all(self) -> None:
        """Clear all context."""
        self.agent_id = None
        self.agent_name = None
        self.conversation_id = None
        self.conversation_title = None
        self.organization_id = None
        self.organization_name = None
        self._save()

    def to_dict(self) -> Dict[str, Any]:
        """Return context as a dictionary."""
        return {
            "agent": {
                "id": self.agent_id,
                "name": self.agent_name,
            }
            if self.agent_id
            else None,
            "conversation": {
                "id": self.conversation_id,
                "title": self.conversation_title,
            }
            if self.conversation_id
            else None,
            "organization": {
                "id": self.organization_id,
                "name": self.organization_name,
            }
            if self.organization_id
            else None,
        }


# Global context instance
_context: Optional[Context] = None


def get_context() -> Context:
    """Get the global context instance."""
    global _context
    if _context is None:
        _context = Context()
    return _context


def set_context(ctx: Context) -> None:
    """Set the global context instance."""
    global _context
    _context = ctx


def clear_context() -> None:
    """Clear the global context."""
    ctx = get_context()
    ctx.clear_all()
