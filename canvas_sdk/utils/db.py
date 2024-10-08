from urllib import parse


def parse_database_url(url: str) -> dict[str, str]:
    """Parses a database URL and returns it in the format expected in Django settings."""
    parsed_url = parse.urlparse(url)
    netloc_split = parsed_url.netloc.split(":")
    db_username = netloc_split[0]
    db_port = netloc_split[2]
    db_password, db_host = netloc_split[1].split("@")
    db_name = parsed_url.path[1:]
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,
        "USER": db_username,
        "PASSWORD": db_password,
        "HOST": db_host,
        "PORT": db_port,
    }
