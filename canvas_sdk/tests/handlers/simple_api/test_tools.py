from collections.abc import Callable
from typing import TypeVar

import pytest

from canvas_sdk.handlers.simple_api.tools import CaseInsensitiveMultiDict, MultiDict
from canvas_sdk.tests.shared import params_from_dict

T = TypeVar("T")


@pytest.mark.parametrize(
    (
        "func",
        "expected_value",
    ),
    params_from_dict(
        {
            "[] single value from single value": (lambda m: m["b"], 2),
            "[] single value from multiple values": (lambda m: m["a"], 1),
            "len": (lambda m: len(m), 2),
            "iter": (lambda m: next(iter(m.items())), ("a", 1)),
            "in": (lambda m: "a" in m, True),
            "not in": (lambda m: "d" in m, False),
            "get": (lambda m: m.get("a"), 1),
            "get default": (lambda m: m.get("d", 4), 4),
            "get no default": (lambda m: m.get("d"), None),
            "get_list": (lambda m: m.get_list("a"), [1, 3]),
            "items": (
                lambda m: [(k, v) for k, v in m.items()],
                [("a", 1), ("b", 2)],
            ),
            "multi_items": (
                lambda m: [(k, v) for k, v in m.multi_items()],
                [("a", 1), ("b", 2), ("a", 3)],
            ),
            "keys": (lambda m: list(m.keys()), ["a", "b"]),
            "reversed": (lambda m: list(reversed(m)), ["b", "a"]),
            "values": (lambda m: list(m.values()), [1, 2]),
            "==": (lambda m: m == MultiDict((("a", 1), ("b", 2), ("a", 3))), True),
            "!=": (lambda m: m != MultiDict((("a", 1), ("b", 2))), True),
        }
    ),
)
def test_multidict(func: Callable[[MultiDict[str, int]], T], expected_value: T) -> None:
    """Test the methods and functionality of MultiDict."""
    multidict = MultiDict((("a", 1), ("b", 2), ("a", 3)))
    assert func(multidict) == expected_value


@pytest.mark.parametrize(
    ("func", "expected_value"),
    params_from_dict(
        {
            "[]": (lambda m: m["b"] == m["B"] == 2, True),
            "in": (lambda m: "a" in m and "A" in m, True),
            "not in": (lambda m: "d" not in m and "D" not in m, True),
            "get": (lambda m: m.get("a") == m.get("A") == 1, True),
            "get_list": (lambda m: m.get_list("a") == m.get_list("A") == [1, 3], True),
        }
    ),
)
def test_case_insensitive_multidict(
    func: Callable[[MultiDict[str, int]], T], expected_value: T
) -> None:
    """Test the methods and functionality of CaseInsensitiveMultiDict."""
    multidict = CaseInsensitiveMultiDict((("a", 1), ("b", 2), ("A", 3)))
    assert func(multidict) == expected_value
