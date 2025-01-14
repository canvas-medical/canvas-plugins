import os

from logger import log

log.info(f"This is a forbidden import. {os}")


def import_me() -> str:
    """Test method."""
    return "Successfully imported!"
