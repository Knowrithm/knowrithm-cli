"""HTTP client utilities for interacting with the Knowrithm backend."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import click
import requests

from . import config


class KnowrithmAPIError(click.ClickException):
    """Raised when the backend returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        prefix = f"[HTTP {status_code}] " if status_code is not None else ""
        super().__init__(prefix + message)
        self.status_code = status_code


class KnowrithmClient:
    """Thin helper around ``requests`` that injects CLI configuration."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
    ) -> None:
        cfg = config.load_config()
        self.base_url = (base_url or cfg.get("base_url") or "").rstrip("/")
        if not self.base_url:
            raise click.ClickException(
                "API base URL is not configured. Run `knowrithm config set-base-url <url>`."
            )
        if verify_ssl is None:
            verify_ssl = cfg.get("verify_ssl", True)
        self.verify_ssl = bool(verify_ssl)
        self.jwt_tokens = cfg.get("auth", {}).get("jwt", {}) or {}
        self.api_credentials = cfg.get("auth", {}).get("api_key", {}) or {}

    # ------------------------------------------------------------------ helpers
    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _prepare_headers(
        self,
        *,
        headers: Optional[Dict[str, str]] = None,
        use_jwt: bool = False,
        use_api_key: bool = False,
    ) -> Dict[str, str]:
        headers = {**(headers or {})}
        if use_jwt:
            token = self.jwt_tokens.get("access_token")
            if token:
                headers.setdefault("Authorization", f"Bearer {token}")
        if use_api_key:
            key = self.api_credentials.get("key")
            secret = self.api_credentials.get("secret")
            if not key or not secret:
                raise click.ClickException(
                    "API key authentication requested but no credentials are configured. "
                    "Set them via `knowrithm auth set-api-key`."
                )
            headers.setdefault("X-API-Key", key)
            headers.setdefault("X-API-Secret", secret)
        headers.setdefault("Accept", "application/json")
        return headers

    def _handle_error(self, response: requests.Response) -> None:
        status = response.status_code
        message = response.text
        try:
            data = response.json()
            # Common API error envelope keys
            for key in ("error", "message", "detail"):
                if data.get(key):
                    message = data[key]
                    break
        except json.JSONDecodeError:
            pass
        raise KnowrithmAPIError(str(message).strip() or "Unknown error", status)

    # ----------------------------------------------------------------- requests
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        use_jwt: Optional[bool] = None,
        use_api_key: Optional[bool] = None,
        require_auth: bool = True,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        # Auto-detect authentication method if not explicitly specified
        if require_auth and (use_jwt is None or use_api_key is None):
            # Default to JWT if available, otherwise API key
            has_jwt = bool(self.jwt_tokens.get("access_token"))
            has_api_key = bool(self.api_credentials.get("key") and self.api_credentials.get("secret"))
            
            if use_jwt is None:
                use_jwt = has_jwt
            if use_api_key is None:
                use_api_key = not has_jwt and has_api_key
            
            # Raise error if authentication is required but no credentials are available
            if require_auth and not (use_jwt or use_api_key):
                raise click.ClickException(
                    "Authentication required but no credentials configured. "
                    "Use 'knowrithm auth login' or 'knowrithm auth set-api-key'."
                )
        headers = self._prepare_headers(headers=headers, use_jwt=use_jwt, use_api_key=use_api_key)
        url = self._build_url(path)
        response = requests.request(
            method.upper(),
            url,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
            verify=self.verify_ssl,
            timeout=timeout,
        )
        if response.status_code >= 400:
            self._handle_error(response)
        return response

    # Convenience wrappers -----------------------------------------------------
    def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.request("GET", path, **kwargs)
        return self._maybe_json(response)

    def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.request("POST", path, **kwargs)
        return self._maybe_json(response)

    def put(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.request("PUT", path, **kwargs)
        return self._maybe_json(response)

    def patch(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.request("PATCH", path, **kwargs)
        return self._maybe_json(response)

    def delete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.request("DELETE", path, **kwargs)
        if response.content:
            return self._maybe_json(response)
        return {"status": "success"}

    # Helpers ------------------------------------------------------------------
    def _maybe_json(self, response: requests.Response) -> Dict[str, Any]:
        if not response.content:
            return {}
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        return {"raw": response.text}

    def handle_async_response(
        self,
        result: Dict[str, Any],
        *,
        wait: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> Dict[str, Any]:
        """Handle asynchronous 202 responses (with optional wait)."""
        if not wait:
            return result
        task_id = result.get("task_id")
        if not task_id:
            return result
        return self.wait_for_task(
            task_id,
            poll_interval=poll_interval,
            timeout=timeout,
        )

    def wait_for_task(
        self,
        task_id: str,
        *,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> Dict[str, Any]:
        """Poll the task status endpoint until completion."""
        from rich.console import Console
        from rich.spinner import Spinner
        from rich.live import Live
        
        console = Console()
        elapsed = 0.0
        
        with Live(Spinner("dots", text="[cyan]Agent is thinking...[/cyan]"), console=console, refresh_per_second=10) as live:
            while True:
                response = self.get(
                    f"/api/v1/tasks/{task_id}/status",
                    require_auth=False,
                    use_jwt=False,
                )
                state = response.get("state") or response.get("status")
                if state in {"SUCCESS", "completed", "finished"}:
                    live.stop()
                    return response.get("result") or response
                if state in {"FAILURE", "failed", "error"}:
                    live.stop()
                    raise KnowrithmAPIError(
                        response.get("error") or response.get("message") or f"Task {task_id} failed.",
                    )
                if timeout and elapsed >= timeout:
                    live.stop()
                    raise KnowrithmAPIError(f"Timed out waiting for task {task_id}.")
                time.sleep(poll_interval)
                elapsed += poll_interval
