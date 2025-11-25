"""System level helper commands."""

from __future__ import annotations

import click

from ..core.formatters import format_output
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="system")
def cmd() -> None:
    """Health checks and global utilities."""


@cmd.command("health")
@format_option()
def health(format: str) -> None:
    """Call the /api/health endpoint."""
    client = make_client()
    response = client.get("/api/health", require_auth=False, use_jwt=False)
    click.echo(format_output(response, format))


@cmd.command("task-status")
@format_option()
@click.argument("task_id")
def task_status(format: str, task_id: str) -> None:
    """Poll task status."""
    client = make_client()
    response = client.get(
        f"/api/v1/tasks/{task_id}/status",
        require_auth=False,
        use_jwt=False,
    )
    click.echo(format_output(response, format))


@cmd.command("address-seed")
@format_option()
def address_seed(format: str) -> None:
    """Trigger address seed data population."""
    client = make_client()
    response = client.get("/api/v1/address-seed", require_auth=False, use_jwt=False)
    click.echo(format_output(response, format))


@cmd.command("countries")
@auth_option()
@format_option()
def countries(auth: str, format: str) -> None:
    """List countries."""
    client = make_client()
    response = client.get("/api/v1/country", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("country")
@auth_option()
@format_option()
@click.argument("country_id")
def country(auth: str, format: str, country_id: str) -> None:
    """Get a country by ID."""
    client = make_client()
    response = client.get(f"/api/v1/country/{country_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("states")
@auth_option()
@format_option()
@click.argument("country_id")
def states(auth: str, format: str, country_id: str) -> None:
    """List states for a country."""
    client = make_client()
    response = client.get(
        f"/api/v1/state/country/{country_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("state")
@auth_option()
@format_option()
@click.argument("state_id")
def state(auth: str, format: str, state_id: str) -> None:
    """Get a state and its cities."""
    client = make_client()
    response = client.get(f"/api/v1/state/{state_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("cities")
@auth_option()
@format_option()
@click.argument("state_id")
def cities(auth: str, format: str, state_id: str) -> None:
    """List cities for a state."""
    client = make_client()
    response = client.get(
        f"/api/v1/city/state/{state_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("city")
@auth_option()
@format_option()
@click.argument("city_id")
def city(auth: str, format: str, city_id: str) -> None:
    """Get a city by ID."""
    client = make_client()
    response = client.get(f"/api/v1/city/{city_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))
