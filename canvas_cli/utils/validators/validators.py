from jsonschema import validate

from canvas_cli.utils.context import context
from canvas_cli.utils.validators.manifest_schema import manifest_schema


def get_default_host(host: str | None) -> str | None:
    """Return context's default host if the host param is null."""
    return host or context.default_host  # type: ignore


def validate_manifest_file(json: dict) -> None:
    """Validates a Canvas Manifest json against the manifest schema."""
    validate(json, manifest_schema)
