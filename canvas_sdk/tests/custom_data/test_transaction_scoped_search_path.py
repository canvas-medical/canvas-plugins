"""Tests that namespace search_path is transaction-scoped.

The plugin runner reaches Postgres through pgdog in transaction mode, where one
Postgres session serves many clients one transaction at a time. These tests
verify that plugin_database_context never sets search_path at session level and
that every query made in a namespace carries its own namespace's search_path
inside the query's transaction.
"""

import os
import threading
from collections.abc import Generator
from typing import Any
from unittest.mock import patch
from urllib import parse

import django.db
import pytest
from django.db import connection, transaction

from canvas_sdk.v1 import plugin_database_context as pdc
from canvas_sdk.v1.plugin_database_context import plugin_database_context

Record = tuple[str, str, bool]


@pytest.fixture
def applied() -> Generator[list[Record], None, None]:
    """Pretend to be PostgreSQL and record every search_path application.

    Each record is (thread name, schema, whether a transaction was open).
    SQLite has no set_config, so the application itself is recorded, not run.
    """
    records: list[Record] = []
    lock = threading.Lock()

    def record(cursor: Any, schema: str) -> None:
        with lock:
            records.append((threading.current_thread().name, schema, connection.in_atomic_block))

    with (
        patch.object(pdc, "_is_postgres", return_value=True),
        patch.object(pdc, "_apply_local_search_path", side_effect=record),
    ):
        yield records


def _query() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()


def test_search_path_sql_is_transaction_local() -> None:
    """The statement passes is_local=true, so Postgres reverts it at transaction end."""
    assert pdc.SET_LOCAL_SEARCH_PATH_SQL == "SELECT set_config('search_path', %s, true)"
    assert pdc._search_path_value("org__a") == '"org__a", public'


@pytest.mark.django_db(transaction=True)
def test_namespace_query_runs_inside_transaction(applied: list[Record]) -> None:
    """A query in a namespace applies the search_path inside a transaction."""
    with plugin_database_context("plugin_a", namespace="org__a"):
        _query()
        _query()

    name = threading.current_thread().name
    assert applied == [(name, "org__a", True), (name, "org__a", True)]


@pytest.mark.django_db(transaction=True)
def test_no_namespace_leaves_queries_alone(applied: list[Record]) -> None:
    """Without a namespace, queries are not wrapped."""
    with plugin_database_context("plugin_a"):
        _query()

    assert applied == []


@pytest.mark.django_db(transaction=True)
def test_queries_after_context_are_not_scoped(applied: list[Record]) -> None:
    """Nothing is applied once the context exits, so nothing needs resetting."""
    with plugin_database_context("plugin_a", namespace="org__a"):
        _query()
    _query()

    assert [schema for _, schema, _ in applied] == ["org__a"]


@pytest.mark.django_db(transaction=True)
def test_existing_transaction_is_reused(applied: list[Record]) -> None:
    """Inside a plugin's own transaction, each query re-applies the path in that transaction."""
    with transaction.atomic(), plugin_database_context("plugin_a", namespace="org__a"):
        _query()
        _query()

    assert [(schema, in_txn) for _, schema, in_txn in applied] == [
        ("org__a", True),
        ("org__a", True),
    ]


@pytest.mark.django_db(transaction=True)
def test_nested_context_uses_innermost_namespace(applied: list[Record]) -> None:
    """Nested contexts apply the inner namespace, then the outer one again."""
    with plugin_database_context("outer", namespace="org__outer"):
        _query()
        with plugin_database_context("inner", namespace="org__inner"):
            _query()
        _query()

    # The outer wrapper stays installed around the inner one, so the inner
    # query applies both paths; the innermost application runs last and wins.
    assert [schema for _, schema, _ in applied] == [
        "org__outer",
        "org__inner",
        "org__inner",
        "org__outer",
    ]


@pytest.mark.django_db(transaction=True)
def test_interleaved_plugins_only_apply_their_own_namespace(applied: list[Record]) -> None:
    """Two plugins alternating queries each run with only their own search_path."""
    rounds = 5
    barrier = threading.Barrier(2)
    errors: list[BaseException] = []

    def plugin(name: str, namespace: str) -> None:
        try:
            with plugin_database_context(name, namespace=namespace):
                for _ in range(rounds):
                    barrier.wait()
                    _query()
        except BaseException as e:
            errors.append(e)
            barrier.abort()

    threads = [
        threading.Thread(target=plugin, args=("plugin_a", "org__a"), name="thread_a"),
        threading.Thread(target=plugin, args=("plugin_b", "org__b"), name="thread_b"),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert sorted({(thread, schema) for thread, schema, _ in applied}) == [
        ("thread_a", "org__a"),
        ("thread_b", "org__b"),
    ]
    assert all(in_txn for _, _, in_txn in applied)
    assert len(applied) == 2 * rounds


@pytest.fixture
def postgres_connection() -> Generator[None, None, None]:
    """Point the default connection at the real PostgreSQL from DATABASE_URL."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is not set")

    parsed = parse.urlparse(database_url)
    handler = django.db.utils.ConnectionHandler(
        {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": parsed.path[1:],
                "USER": parsed.username,
                "PASSWORD": parsed.password,
                "HOST": parsed.hostname,
                "PORT": parsed.port,
            }
        }
    )
    original = django.db.connections["default"]
    django.db.connections["default"] = handler["default"]
    try:
        with patch.object(pdc, "_is_postgres", return_value=True):
            yield
    finally:
        django.db.connections["default"].close()
        django.db.connections["default"] = original


def _show_search_path() -> str:
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        return str(cursor.fetchone()[0])


@pytest.mark.integtest
@pytest.mark.django_db
def test_postgres_interleaved_plugins_share_a_session_without_leaking(
    postgres_connection: None,
) -> None:
    """Two plugins alternating on ONE Postgres session never see each other's path.

    Sharing a single session between clients is what a transaction-mode pooler
    does, so this is the leak scenario without needing the pooler itself.
    """
    baseline = _show_search_path()

    for _ in range(3):
        with plugin_database_context("plugin_a", namespace="org__a"):
            path_a = _show_search_path()
        between = _show_search_path()
        with plugin_database_context("plugin_b", namespace="org__b"):
            path_b = _show_search_path()

        assert "org__a" in path_a and "org__b" not in path_a
        assert "org__b" in path_b and "org__a" not in path_b
        assert between == baseline

    assert _show_search_path() == baseline
