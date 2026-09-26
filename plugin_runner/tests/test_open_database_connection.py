"""Tests for plugin_runner.namespace.open_database_connection URL selection."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from plugin_runner.namespace import open_database_connection


@pytest.fixture
def mock_connect(mocker: MockerFixture) -> MagicMock:
    """Replace psycopg.connect so no real connection is opened."""
    return mocker.patch("plugin_runner.namespace.psycopg.connect")


def test_bouncer_url_takes_precedence_over_database_url(
    monkeypatch: pytest.MonkeyPatch,
    mock_connect: MagicMock,
) -> None:
    """The pgdog bouncer URL is used when both it and DATABASE_URL are set."""
    monkeypatch.setenv("DATABASE_URL", "postgres://direct:pw@db.example.com:5432/home-app")
    monkeypatch.setenv(
        "CANVAS_PLUGINS_BOUNCER_DATABASE_URL", "postgres://direct:pw@127.0.0.1:6432/home-app"
    )

    open_database_connection()

    mock_connect.assert_called_once_with(
        dbname="home-app",
        user="direct",
        password="pw",
        host="127.0.0.1",
        port=6432,
    )


def test_database_url_used_without_bouncer_url(
    monkeypatch: pytest.MonkeyPatch,
    mock_connect: MagicMock,
) -> None:
    """DATABASE_URL is used when the bouncer URL is unset."""
    monkeypatch.delenv("CANVAS_PLUGINS_BOUNCER_DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgres://direct:pw@db.example.com:5432/home-app")

    open_database_connection()

    mock_connect.assert_called_once_with(
        dbname="home-app",
        user="direct",
        password="pw",
        host="db.example.com",
        port=5432,
    )
