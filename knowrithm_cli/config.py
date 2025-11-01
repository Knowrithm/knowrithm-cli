"""Configuration helpers for the Knowrithm CLI.

The CLI keeps user configuration (API base URL, authentication tokens, etc.)
under ``~/.knowrithm/config.json``.  This module provides small convenience
helpers for reading and mutating that file while hiding filesystem details
from the command implementations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_DIR = Path.home() / ".knowrithm"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "base_url": None,
    "verify_ssl": True,
    "auth": {
        "jwt": {},
        "api_key": {},
    },
}


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Return the persisted configuration, falling back to defaults."""
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {CONFIG_FILE}: {exc}") from exc
        merged = DEFAULT_CONFIG.copy()
        merged["auth"] = DEFAULT_CONFIG["auth"].copy()
        merged.update({k: v for k, v in data.items() if k != "auth"})
        if isinstance(data.get("auth"), dict):
            merged["auth"].update(data["auth"])
        return merged
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Persist the given configuration dictionary."""
    _ensure_dir()
    with CONFIG_FILE.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, sort_keys=True)


def update_config(**updates: Any) -> Dict[str, Any]:
    """Merge primitive updates into the configuration and persist."""
    config = load_config()
    config.update(updates)
    save_config(config)
    return config


def set_base_url(url: str) -> Dict[str, Any]:
    """Set the API base URL."""
    url = url.rstrip("/")
    return update_config(base_url=url or None)


def set_verify_ssl(enabled: bool) -> Dict[str, Any]:
    """Enable/disable TLS certificate verification."""
    return update_config(verify_ssl=bool(enabled))


def store_jwt_tokens(
    access_token: str,
    refresh_token: Optional[str] = None,
    *,
    expires_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist JWT tokens under the auth section."""
    config = load_config()
    jwt_block = config.setdefault("auth", {}).get("jwt", {})
    jwt_block.update(
        {
            "access_token": access_token,
        }
    )
    if refresh_token is not None:
        jwt_block["refresh_token"] = refresh_token
    if expires_at is not None:
        jwt_block["expires_at"] = expires_at
    config["auth"]["jwt"] = jwt_block
    save_config(config)
    return config


def clear_jwt_tokens() -> Dict[str, Any]:
    """Remove cached JWT tokens."""
    config = load_config()
    config.setdefault("auth", {})["jwt"] = {}
    save_config(config)
    return config


def store_api_credentials(api_key: str, api_secret: str) -> Dict[str, Any]:
    """Persist the API key/secret pair."""
    config = load_config()
    config.setdefault("auth", {})["api_key"] = {
        "key": api_key,
        "secret": api_secret,
    }
    save_config(config)
    return config


def clear_api_credentials() -> Dict[str, Any]:
    """Remove stored API credentials."""
    config = load_config()
    config.setdefault("auth", {})["api_key"] = {}
    save_config(config)
    return config


def get_base_url() -> Optional[str]:
    """Convenience accessor for the configured base URL."""
    return load_config().get("base_url")


def get_verify_ssl() -> bool:
    """Return whether HTTPS requests should verify TLS certificates."""
    return bool(load_config().get("verify_ssl", True))


def get_jwt_tokens() -> Dict[str, Any]:
    """Return the JWT token block."""
    return load_config().get("auth", {}).get("jwt", {})


def get_api_credentials() -> Dict[str, Any]:
    """Return the stored API key credentials."""
    return load_config().get("auth", {}).get("api_key", {})

