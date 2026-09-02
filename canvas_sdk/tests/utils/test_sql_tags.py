"""Tests for the canvas_sdk.utils.sql_tags shim."""

import pytest

from canvas_sdk.utils.sql_tags import query_tags


def test_query_tags_is_a_context_manager() -> None:
    """query_tags() must be usable as a `with`-block regardless of whether
    home-app is on the import path.
    """
    with query_tags(plugin="example", event="EVENT", handler="h.compute"):
        pass


def test_query_tags_propagates_exceptions() -> None:
    """An exception raised inside the block must surface to the caller and
    must not leak any global state.
    """

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom), query_tags(plugin="example"):
        raise _Boom("from inside")
