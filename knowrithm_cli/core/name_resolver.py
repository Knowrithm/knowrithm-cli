"""Name resolution utilities for the Knowrithm CLI.

Resolves human-friendly names to UUIDs with caching and fuzzy matching.
"""

from __future__ import annotations

import json
from difflib import get_close_matches
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from .. import config

CACHE_FILE = config.CONFIG_DIR / "name_cache.json"


class NameResolver:
    """Resolves names to IDs with caching and fuzzy matching."""

    def __init__(self, client: Any) -> None:
        self.client = client
        self.cache: Dict[str, Dict[str, str]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Dict[str, str]]:
        """Load name-to-ID cache from disk."""
        if CACHE_FILE.exists():
            try:
                with CACHE_FILE.open("r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, IOError):
                pass
        return {"agents": {}, "conversations": {}, "databases": {}, "companies": {}}

    def _save_cache(self) -> None:
        """Persist cache to disk."""
        config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with CACHE_FILE.open("w", encoding="utf-8") as fh:
            json.dump(self.cache, fh, indent=2)

    def _update_cache(self, category: str, name: str, id_value: str) -> None:
        """Update cache with a name-to-ID mapping."""
        if category not in self.cache:
            self.cache[category] = {}
        self.cache[category][name.lower()] = id_value
        self._save_cache()

    def _fuzzy_match(self, category: str, name: str) -> Optional[str]:
        """Attempt fuzzy matching on cached names."""
        if category not in self.cache:
            return None
        names = list(self.cache[category].keys())
        matches = get_close_matches(name.lower(), names, n=1, cutoff=0.6)
        if matches:
            matched_name = matches[0]
            click.echo(
                f"Did you mean '{matched_name}'? Using that instead of '{name}'.",
                err=True,
            )
            return self.cache[category][matched_name]
        return None

    def resolve_agent(
        self, name_or_id: str, *, use_cache: bool = True, fuzzy: bool = True
    ) -> str:
        """Resolve agent name to ID.

        Args:
            name_or_id: Agent name or UUID
            use_cache: Whether to check cache first
            fuzzy: Whether to use fuzzy matching

        Returns:
            Agent UUID

        Raises:
            click.ClickException: If agent not found
        """
        # If it looks like a UUID, return as-is
        if self._is_uuid(name_or_id):
            return name_or_id

        # Check cache
        if use_cache:
            cached_id = self.cache.get("agents", {}).get(name_or_id.lower())
            if cached_id:
                return cached_id

        # Query API
        try:
            response = self.client.get(
                f"/api/v1/agent/by-name/{name_or_id}",
                require_auth=True,
            )
            if response and "id" in response:
                agent_id = response["id"]
                agent_name = response.get("name", name_or_id)
                self._update_cache("agents", agent_name, agent_id)
                return agent_id
        except Exception:
            pass

        # Try fuzzy matching
        if fuzzy:
            fuzzy_id = self._fuzzy_match("agents", name_or_id)
            if fuzzy_id:
                return fuzzy_id

        raise click.ClickException(
            f"Agent '{name_or_id}' not found. Use 'knowrithm agent list' to see available agents."
        )

    def resolve_conversation(
        self, name_or_id: str, *, use_cache: bool = True, fuzzy: bool = True
    ) -> str:
        """Resolve conversation name/title to ID.

        Args:
            name_or_id: Conversation title or UUID
            use_cache: Whether to check cache first
            fuzzy: Whether to use fuzzy matching

        Returns:
            Conversation UUID

        Raises:
            click.ClickException: If conversation not found
        """
        if self._is_uuid(name_or_id):
            return name_or_id

        if use_cache:
            cached_id = self.cache.get("conversations", {}).get(name_or_id.lower())
            if cached_id:
                return cached_id

        # Query API - list conversations and find by title
        try:
            response = self.client.get(
                "/api/v1/conversation",
                params={"per_page": 100},
                require_auth=True,
            )
            conversations = response.get("data", [])
            for conv in conversations:
                title = conv.get("title", "")
                if title.lower() == name_or_id.lower():
                    conv_id = conv["id"]
                    self._update_cache("conversations", title, conv_id)
                    return conv_id
        except Exception:
            pass

        if fuzzy:
            fuzzy_id = self._fuzzy_match("conversations", name_or_id)
            if fuzzy_id:
                return fuzzy_id

        raise click.ClickException(
            f"Conversation '{name_or_id}' not found. Use 'knowrithm conversation list' to see available conversations."
        )

    def resolve_database(
        self, name_or_id: str, *, use_cache: bool = True, fuzzy: bool = True
    ) -> str:
        """Resolve database connection name to ID.

        Args:
            name_or_id: Database name or UUID
            use_cache: Whether to check cache first
            fuzzy: Whether to use fuzzy matching

        Returns:
            Database connection UUID

        Raises:
            click.ClickException: If database not found
        """
        if self._is_uuid(name_or_id):
            return name_or_id

        if use_cache:
            cached_id = self.cache.get("databases", {}).get(name_or_id.lower())
            if cached_id:
                return cached_id

        # Query API
        try:
            response = self.client.get(
                "/api/v1/database-connection",
                require_auth=True,
            )
            connections = response.get("data", []) if isinstance(response, dict) else response
            for conn in connections:
                name = conn.get("name", "")
                if name.lower() == name_or_id.lower():
                    conn_id = conn["id"]
                    self._update_cache("databases", name, conn_id)
                    return conn_id
        except Exception:
            pass

        if fuzzy:
            fuzzy_id = self._fuzzy_match("databases", name_or_id)
            if fuzzy_id:
                return fuzzy_id

        raise click.ClickException(
            f"Database '{name_or_id}' not found. Use 'knowrithm database list' to see available connections."
        )

    def resolve_company(
        self, name_or_id: str, *, use_cache: bool = True, fuzzy: bool = True
    ) -> str:
        """Resolve company name to ID (super admin only).

        Args:
            name_or_id: Company name or UUID
            use_cache: Whether to check cache first
            fuzzy: Whether to use fuzzy matching

        Returns:
            Company UUID

        Raises:
            click.ClickException: If company not found
        """
        if self._is_uuid(name_or_id):
            return name_or_id

        if use_cache:
            cached_id = self.cache.get("companies", {}).get(name_or_id.lower())
            if cached_id:
                return cached_id

        # Query API
        try:
            response = self.client.get(
                "/api/v1/super-admin/company",
                params={"per_page": 100},
                require_auth=True,
                use_jwt=True,
            )
            companies = response.get("data", [])
            for company in companies:
                name = company.get("name", "")
                if name.lower() == name_or_id.lower():
                    company_id = company["id"]
                    self._update_cache("companies", name, company_id)
                    return company_id
        except Exception:
            pass

        if fuzzy:
            fuzzy_id = self._fuzzy_match("companies", name_or_id)
            if fuzzy_id:
                return fuzzy_id

        raise click.ClickException(
            f"Company '{name_or_id}' not found. Use 'knowrithm superadmin companies list' to see available companies."
        )

    def clear_cache(self, category: Optional[str] = None) -> None:
        """Clear the name cache.

        Args:
            category: Specific category to clear, or None for all
        """
        if category:
            if category in self.cache:
                self.cache[category] = {}
        else:
            self.cache = {"agents": {}, "conversations": {}, "databases": {}, "companies": {}}
        self._save_cache()

    @staticmethod
    def _is_uuid(value: str) -> bool:
        """Check if a string looks like a UUID."""
        # Simple check: UUIDs are 36 chars with hyphens at specific positions
        if len(value) != 36:
            return False
        parts = value.split("-")
        if len(parts) != 5:
            return False
        lengths = [len(p) for p in parts]
        return lengths == [8, 4, 4, 4, 12]
