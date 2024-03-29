from jsonschema import validate

from canvas_cli.apps.auth.utils import get_password
from canvas_cli.utils.context import context
from canvas_cli.utils.validators.manifest_schema import manifest_schema


def get_default_host(host: str | None) -> str | None:
    """Return context's default host if the host param is null."""
    return host or context.default_host


def get_api_key(host: str, api_key: str | None) -> str | None:
    """Either return the given api_key, or fetch it from the keyring."""
    match host, api_key:
        case (host, None):
            return get_password(host)
        case (_, api_key):
            return api_key

    return None


def validate_manifest_file(json: dict) -> None:
    """Validates a Canvas Manifest json against the manifest schema."""
    validate(json, manifest_schema)
