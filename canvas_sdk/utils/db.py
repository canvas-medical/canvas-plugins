from typing import Any
from urllib import parse


def parse_database_url(url: str) -> dict[str, Any]:
    """Parses a database URL and returns it in the format expected in Django settings."""
    parsed_url = parse.urlparse(url)
    db_name = parsed_url.path[1:]
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,
        "USER": parsed_url.username,
        "PASSWORD": parsed_url.password,
        "HOST": parsed_url.hostname,
        "PORT": parsed_url.port,
    }
