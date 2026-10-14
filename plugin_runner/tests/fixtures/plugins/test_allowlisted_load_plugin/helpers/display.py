import re


def is_match(value) -> str:  # type: ignore[no-untyped-def]
    """Check a value against the match type, as a command display helper does."""
    return str(isinstance(value, re.Match))
