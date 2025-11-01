"""System level helper commands."""

from __future__ import annotations

import click

from ..utils import print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="system")
def cmd() -> None:
    """Health checks and global utilities."""


@cmd.command("health")
def health() -> None:
    """Call the /api/health endpoint."""
    client = make_client()
    response = client.get("/api/health", require_auth=False, use_jwt=False)
    print_json(response)


@cmd.command("task-status")
@click.argument("task_id")
def task_status(task_id: str) -> None:
    """Poll task status."""
    client = make_client()
    response = client.get(
        f"/api/v1/tasks/{task_id}/status",
        require_auth=False,
        use_jwt=False,
    )
    print_json(response)


@cmd.command("address-seed")
def address_seed() -> None:
    """Trigger address seed data population."""
    client = make_client()
    response = client.get("/api/v1/address-seed", require_auth=False, use_jwt=False)
    print_json(response)


@cmd.command("countries")
@auth_option()
def countries(auth: str) -> None:
    """List countries."""
    client = make_client()
    response = client.get("/api/v1/country", **auth_kwargs(auth))
    print_json(response)


@cmd.command("country")
@auth_option()
@click.argument("country_id")
def country(auth: str, country_id: str) -> None:
    """Get a country by ID."""
    client = make_client()
    response = client.get(f"/api/v1/country/{country_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("states")
@auth_option()
@click.argument("country_id")
def states(auth: str, country_id: str) -> None:
    """List states for a country."""
    client = make_client()
    response = client.get(
        f"/api/v1/state/country/{country_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("state")
@auth_option()
@click.argument("state_id")
def state(auth: str, state_id: str) -> None:
    """Get a state and its cities."""
    client = make_client()
    response = client.get(f"/api/v1/state/{state_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("cities")
@auth_option()
@click.argument("state_id")
def cities(auth: str, state_id: str) -> None:
    """List cities for a state."""
    client = make_client()
    response = client.get(
        f"/api/v1/city/state/{state_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("city")
@auth_option()
@click.argument("city_id")
def city(auth: str, city_id: str) -> None:
    """Get a city by ID."""
    client = make_client()
    response = client.get(f"/api/v1/city/{city_id}", **auth_kwargs(auth))
    print_json(response)

