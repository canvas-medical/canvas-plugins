"""Tests for plugin_runner.namespace.open_database_connection URL selection."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from plugin_runner.namespace import open_database_connection


@pytest.fixture
def mock_connect(mocker: MockerFixture) -> MagicMock:
    """Replace psycopg.connect so no real connection is opened."""
    return mocker.patch("plugin_runner.namespace.psycopg.connect")


def test_bouncer_url_is_ignored(
    monkeypatch: pytest.MonkeyPatch,
    mock_connect: MagicMock,
) -> None:
    """Schema management connects straight to Postgres even when the pgdog URL is set.

    wait_for_namespace uses LISTEN, which a transaction-mode pooler cannot serve.
    """
    monkeypatch.setenv("DATABASE_URL", "postgres://direct:pw@db.example.com:5432/home-app")
    monkeypatch.setenv(
        "CANVAS_PLUGINS_BOUNCER_DATABASE_URL", "postgres://direct:pw@127.0.0.1:6432/home-app"
    )

    open_database_connection()

    mock_connect.assert_called_once_with(
        dbname="home-app",
        user="direct",
        password="pw",
        host="db.example.com",
        port=5432,
    )
