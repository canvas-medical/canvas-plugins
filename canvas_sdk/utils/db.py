import os
from typing import Any
from urllib import parse


def get_database_dict_from_url() -> dict[str, Any]:
    """Retrieves the database URL for the data module connection formatted for Django settings."""
    parsed_url = parse.urlparse(os.getenv("DATABASE_URL"))
    db_name = parsed_url.path[1:]
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,
        "USER": os.getenv("CANVAS_SDK_DATABASE_ROLE"),
        "PASSWORD": os.getenv("CANVAS_SDK_DATABASE_ROLE_PASSWORD"),
        "HOST": parsed_url.hostname,
        "PORT": parsed_url.port,
    }
