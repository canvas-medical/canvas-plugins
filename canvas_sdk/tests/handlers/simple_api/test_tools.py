from collections.abc import Callable
from typing import TypeVar

import pytest

from canvas_sdk.handlers.simple_api.tools import CaseInsensitiveMultiDict, MultiDict

T = TypeVar("T")


@pytest.mark.parametrize(
    argnames="func,expected_value",
    argvalues=[
        (lambda m: m["b"], 2),
        (lambda m: m["a"], 1),
        (lambda m: len(m), 2),
        (lambda m: next(iter(m.items())), ("a", 1)),
        (lambda m: "a" in m, True),
        (lambda m: "d" in m, False),
        (lambda m: m.get("a"), 1),
        (lambda m: m.get("d", 4), 4),
        (lambda m: m.get("d"), None),
        (lambda m: m.get_list("a"), [1, 3]),
        (
            lambda m: [(k, v) for k, v in m.items()],
            [("a", 1), ("b", 2)],
        ),
        (
            lambda m: [(k, v) for k, v in m.multi_items()],
            [("a", 1), ("b", 2), ("a", 3)],
        ),
        (lambda m: list(m.keys()), ["a", "b"]),
        (lambda m: list(reversed(m)), ["b", "a"]),
        (lambda m: list(m.values()), [1, 2]),
        (lambda m: m == MultiDict((("a", 1), ("b", 2), ("a", 3))), True),
        (lambda m: m != MultiDict((("a", 1), ("b", 2))), True),
    ],
    ids=[
        "[] single value from single value",
        "[] single value from multiple values",
        "len",
        "iter",
        "in",
        "not in",
        "get",
        "get default",
        "get no default",
        "get_list",
        "items",
        "multi_items",
        "keys",
        "reversed",
        "values",
        "==",
        "!=",
    ],
)
def test_multidict(func: Callable[[MultiDict[str, int]], T], expected_value: T) -> None:
    """Test the methods and functionality of MultiDict."""
    multidict = MultiDict((("a", 1), ("b", 2), ("a", 3)))
    assert func(multidict) == expected_value


@pytest.mark.parametrize(
    argnames="func,expected_value",
    argvalues=[
        (lambda m: m["b"] == m["B"] == 2, True),
        (lambda m: "a" in m and "A" in m, True),
        (lambda m: "d" not in m and "D" not in m, True),
        (lambda m: m.get("a") == m.get("A") == 1, True),
        (lambda m: m.get_list("a") == m.get_list("A") == [1, 3], True),
    ],
    ids=["[]", "in", "not in", "get", "get_list"],
)
def test_case_insensitive_multidict(
    func: Callable[[MultiDict[str, int]], T], expected_value: T
) -> None:
    """Test the methods and functionality of CaseInsensitiveMultiDict."""
    multidict = CaseInsensitiveMultiDict((("a", 1), ("b", 2), ("A", 3)))
    assert func(multidict) == expected_value
