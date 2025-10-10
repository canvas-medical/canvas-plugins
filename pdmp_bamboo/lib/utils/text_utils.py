"""
Text Utilities.

Common text formatting and manipulation utilities.
"""

from typing import Any


def format_full_name(first: str, last: str, middle: str = "") -> str:
    """
    Format full name from parts.

    Args:
        first: First name
        last: Last name
        middle: Middle name (optional)

    Returns:
        Formatted full name string
    """
    if middle:
        parts = [first, middle, last]
    else:
        parts = [first, last]

    return " ".join(filter(None, parts)).strip()


def safe_get(data: dict | None, key: str, default: Any = None) -> Any:
    """
    Safely get value from dict with None/empty dict handling.

    Args:
        data: Dictionary to get value from (can be None)
        key: Key to retrieve
        default: Default value if key not found or data is None

    Returns:
        Value from dict or default
    """
    if data is None:
        return default
    return data.get(key, default)

