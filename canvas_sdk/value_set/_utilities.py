from inspect import isclass
from typing import Any

from canvas_sdk.value_set.value_set import ValueSet


def get_overrides(dictionary: dict[str, Any]) -> tuple:
    """
    Return the keys that are ValueSets.
    """
    return tuple(
        key for key, value in dictionary.items() if isclass(value) and issubclass(value, ValueSet)
    )


__exports__ = ()
