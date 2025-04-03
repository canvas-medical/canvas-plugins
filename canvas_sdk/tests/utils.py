import shutil
from pathlib import Path
from typing import cast

import requests

import settings
from canvas_cli.apps.plugin.plugin import _build_package, plugin_url
from canvas_generated.messages.events_pb2 import Event


class MaskedValue:
    """A class to mask sensitive values in tests."""

    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return "MaskedValue(********)"

    def __str___(self) -> str:
        return "*******"


def install_plugin(plugin_name: str, token: MaskedValue) -> None:
    """Install a plugin."""
    with open(_build_package(Path(f"./custom-plugins/{plugin_name}")), "rb") as package:
        response = requests.post(
            plugin_url(cast(str, settings.INTEGRATION_TEST_URL)),
            data={"is_enabled": True},
            files={"package": package},
            headers={"Authorization": f"Bearer {token.value}"},
        )
        response.raise_for_status()


def trigger_plugin_event(event: Event, token: MaskedValue) -> None:
    """Trigger a plugin event."""
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/plugin-io/test-utils/events/trigger/",
        headers={
            "Authorization": f"Bearer {token.value}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "event": event.SerializeToString().hex(),
        },
    )
    response.raise_for_status()


def clean_up_files_and_plugins(plugin_name: str, token: MaskedValue) -> None:
    """Clean up the files and plugins."""
    # clean up
    if Path(f"./custom-plugins/{plugin_name}").exists():
        shutil.rmtree(Path(f"./custom-plugins/{plugin_name}"))

    # delete
    response = requests.delete(
        plugin_url(cast(str, settings.INTEGRATION_TEST_URL), plugin_name),
        params={"force": True},
        headers={"Authorization": f"Bearer {token.value}"},
    )
    response.raise_for_status()


def create_note(token: MaskedValue) -> dict:
    """Create a new note."""
    data = {
        "patient": 1,
        "provider": 1,
        "note_type": "office",
        "note_type_version": 1,
        "lastModifiedBySessionKey": "8fee3c03a525cebee1d8a6b8e63dd4dg",
    }
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/",
        headers={"Authorization": f"Bearer {token.value}"},
        json=data,
    )
    response.raise_for_status()
    return response.json()
