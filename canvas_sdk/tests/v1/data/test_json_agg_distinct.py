"""Test that DISTINCT fails on views whose columns use json_agg().

PostgreSQL's json_agg() returns the ``json`` type, which has no equality
operator.  Any ``SELECT DISTINCT`` that includes such a column will fail::

    could not identify an equality operator for type json

The fix is to use ``jsonb_agg()`` instead, which returns ``jsonb`` — a type
that *does* support equality.

Affected SDK views (defined in home-app ``plugin_io/database_views.py``):

* ``canvas_sdk_data_api_imagingorder_001``  — ``task_ids`` column
* ``canvas_sdk_data_api_referral_001``      — ``task_ids`` column
"""

import pytest
from django.db import connection


@pytest.fixture()
def _json_agg_view(request: pytest.FixtureRequest) -> None:
    """Create a parent table, a child table, and a view that aggregates
    children with a JSON array function.

    On PostgreSQL the view uses ``json_agg()``; on SQLite it uses the
    equivalent ``json_group_array()``.
    """
    is_pg = connection.vendor == "postgresql"

    with connection.cursor() as cur:
        cur.execute("CREATE TABLE _test_orders (  id INTEGER PRIMARY KEY,  name TEXT)")
        cur.execute(
            "CREATE TABLE _test_tasks ("
            "  id INTEGER PRIMARY KEY,"
            "  order_id INTEGER REFERENCES _test_orders(id)"
            ")"
        )
        cur.execute("INSERT INTO _test_orders VALUES (1, 'order_a')")
        cur.execute("INSERT INTO _test_orders VALUES (2, 'order_b')")
        cur.execute("INSERT INTO _test_tasks VALUES (10, 1)")
        cur.execute("INSERT INTO _test_tasks VALUES (20, 1)")
        cur.execute("INSERT INTO _test_tasks VALUES (30, 2)")

        agg_fn = "json_agg" if is_pg else "json_group_array"
        cur.execute(
            f"CREATE VIEW _test_order_view AS "
            f"SELECT o.id, o.name, "
            f"  (SELECT {agg_fn}(t.id) "
            f"   FROM _test_tasks t WHERE t.order_id = o.id) AS task_ids "
            f"FROM _test_orders o"
        )

    def _teardown() -> None:
        with connection.cursor() as cur:
            cur.execute("DROP VIEW IF EXISTS _test_order_view")
            cur.execute("DROP TABLE IF EXISTS _test_tasks")
            cur.execute("DROP TABLE IF EXISTS _test_orders")

    request.addfinalizer(_teardown)


@pytest.fixture()
def _jsonb_agg_view(request: pytest.FixtureRequest) -> None:
    """Same as ``_json_agg_view`` but using ``jsonb_agg()`` on PostgreSQL.

    PostgreSQL only — on SQLite this is identical to _json_agg_view since
    SQLite has no jsonb_agg function.
    """
    if connection.vendor != "postgresql":
        pytest.skip("jsonb_agg is PostgreSQL-specific")

    with connection.cursor() as cur:
        cur.execute("CREATE TABLE _test_orders_b (  id INTEGER PRIMARY KEY,  name TEXT)")
        cur.execute(
            "CREATE TABLE _test_tasks_b ("
            "  id INTEGER PRIMARY KEY,"
            "  order_id INTEGER REFERENCES _test_orders_b(id)"
            ")"
        )
        cur.execute("INSERT INTO _test_orders_b VALUES (1, 'order_a')")
        cur.execute("INSERT INTO _test_tasks_b VALUES (10, 1)")

        cur.execute(
            "CREATE VIEW _test_order_view_b AS "
            "SELECT o.id, o.name, "
            "  (SELECT jsonb_agg(t.id) "
            "   FROM _test_tasks_b t WHERE t.order_id = o.id) AS task_ids "
            "FROM _test_orders_b o"
        )

    def _teardown() -> None:
        with connection.cursor() as cur:
            cur.execute("DROP VIEW IF EXISTS _test_order_view_b")
            cur.execute("DROP TABLE IF EXISTS _test_tasks_b")
            cur.execute("DROP TABLE IF EXISTS _test_orders_b")

    request.addfinalizer(_teardown)


@pytest.mark.django_db
@pytest.mark.usefixtures("_json_agg_view")
def test_distinct_fails_on_view_with_json_agg() -> None:
    """SELECT DISTINCT on a view with a json_agg column fails in PostgreSQL.

    This reproduces the error seen with ImagingOrder and Referral, whose
    ``task_ids`` column is computed via ``json_agg()`` in the view SQL.

    On SQLite this passes because json_group_array() returns TEXT, which
    supports equality.  On PostgreSQL this fails because json_agg() returns
    the ``json`` type, which has no equality operator.
    """
    with connection.cursor() as cur:
        if connection.vendor == "postgresql":
            with pytest.raises(Exception, match="could not identify an equality operator"):
                cur.execute("SELECT DISTINCT * FROM _test_order_view")
        else:
            # SQLite: json_group_array returns text → DISTINCT works fine.
            cur.execute("SELECT DISTINCT * FROM _test_order_view")
            rows = cur.fetchall()
            assert len(rows) == 2


@pytest.mark.django_db
@pytest.mark.usefixtures("_jsonb_agg_view")
def test_distinct_succeeds_on_view_with_jsonb_agg() -> None:
    """SELECT DISTINCT on a view with a jsonb_agg column works in PostgreSQL.

    ``jsonb_agg()`` returns ``jsonb``, which has equality operators and
    therefore supports DISTINCT.  Replacing ``json_agg`` → ``jsonb_agg``
    in the ImagingOrder and Referral view definitions fixes the issue.
    """
    with connection.cursor() as cur:
        cur.execute("SELECT DISTINCT * FROM _test_order_view_b")
        rows = cur.fetchall()
        assert len(rows) == 1
