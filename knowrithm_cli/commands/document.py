"""Document management commands."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import click

from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="document")
def cmd() -> None:
    """Manage documents and knowledge base entries."""


@cmd.command("list")
@auth_option()
@format_option()
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def list_documents(auth: str, format: str, page: int, per_page: int) -> None:
    """List documents for the current company."""
    client = make_client()
    response = client.get(
        "/api/v1/document",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("agent")
@auth_option()
@format_option()
@click.argument("agent_id")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def agent_documents(auth: str, format: str, agent_id: str, page: int, per_page: int) -> None:
    """List documents linked to an agent."""
    client = make_client()
    response = client.get(
        f"/api/v1/document/agent/{agent_id}",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


def _prepare_file_payload(paths: List[str]):
    handles = []
    files = []
    try:
        for p in paths:
            path = Path(p).expanduser()
            handle = path.open("rb")
            handles.append(handle)
            files.append(
                (
                    "files",
                    (path.name, handle, "application/octet-stream"),
                )
            )
        return files, handles
    except Exception:
        for handle in handles:
            handle.close()
        raise


@cmd.command("upload")
@auth_option()
@format_option()
@click.option("--agent-id", required=True, help="Agent identifier to associate with the upload.")
@click.option("--file", "files_", multiple=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--url", "urls", multiple=True, help="URL(s) to ingest.")
@click.option("--payload", help="Additional JSON fields for the upload request.")
def upload_documents(
    auth: str,
    format: str,
    agent_id: str,
    files_: List[str],
    urls: List[str],
    payload: Optional[str],
) -> None:
    """Upload documents or initiate scraping tasks."""
    extra = load_json_payload(payload) if payload else {}
    if not isinstance(extra, (dict, type(None))):
        raise click.ClickException("Payload must be a JSON object.")
    client = make_client()
    # Determine whether to send multipart/form-data or JSON.
    if files_:
        form = extra.copy() if isinstance(extra, dict) else {}
        form["agent_id"] = agent_id
        if urls:
            form["urls"] = list(urls)
        files_payload, handles = _prepare_file_payload(list(files_))
        try:
            response = client.post(
                "/api/v1/document/upload",
                data=form,
                files=files_payload,
                **auth_kwargs(auth),
            )
        finally:
            for handle in handles:
                handle.close()
    else:
        body = extra.copy() if isinstance(extra, dict) else {}
        body.setdefault("agent_id", agent_id)
        if urls:
            body.setdefault("urls", list(urls))
        response = client.post(
            "/api/v1/document/upload",
            json=body,
            **auth_kwargs(auth),
        )
    click.echo(format_output(response, format))


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("document_id")
def delete_document(auth: str, format: str, document_id: str) -> None:
    """Soft delete a document."""
    client = make_client()
    response = client.delete(f"/api/v1/document/{document_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("restore")
@auth_option()
@format_option()
@click.argument("document_id")
def restore_document(auth: str, format: str, document_id: str) -> None:
    """Restore a soft-deleted document."""
    client = make_client()
    response = client.patch(f"/api/v1/document/{document_id}/restore", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("delete-chunks")
@auth_option()
@format_option()
@click.argument("document_id")
def delete_chunks(auth: str, format: str, document_id: str) -> None:
    """Delete all chunks for a document."""
    client = make_client()
    response = client.delete(
        f"/api/v1/document/{document_id}/chunk",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("restore-chunks")
@auth_option()
@format_option()
@click.argument("document_id")
def restore_chunks(auth: str, format: str, document_id: str) -> None:
    """Restore all chunks for a document."""
    client = make_client()
    response = client.patch(
        f"/api/v1/document/{document_id}/chunk/restore-all",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("delete-chunk")
@auth_option()
@format_option()
@click.argument("chunk_id")
def delete_chunk(auth: str, format: str, chunk_id: str) -> None:
    """Delete a single document chunk."""
    client = make_client()
    response = client.delete(f"/api/v1/document/chunk/{chunk_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("restore-chunk")
@auth_option()
@format_option()
@click.argument("chunk_id")
def restore_chunk(auth: str, format: str, chunk_id: str) -> None:
    """Restore a single document chunk."""
    client = make_client()
    response = client.patch(
        f"/api/v1/document/chunk/{chunk_id}/restore",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("deleted")
@auth_option()
@format_option()
def deleted_documents(auth: str, format: str) -> None:
    """List deleted documents."""
    client = make_client()
    response = client.get("/api/v1/document/deleted", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("deleted-chunks")
@auth_option()
@format_option()
def deleted_chunks(auth: str, format: str) -> None:
    """List deleted document chunks."""
    client = make_client()
    response = client.get("/api/v1/document/chunk/deleted", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("bulk-delete")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload with document_ids.")
def bulk_delete(auth: str, format: str, payload: str) -> None:
    """Bulk delete documents."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.delete("/api/v1/document/bulk-delete", json=body, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("search")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON search payload.")
def search(auth: str, format: str, payload: str) -> None:
    """Run semantic document search."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/search/document", json=body, **auth_kwargs(auth))
    click.echo(format_output(response, format))
