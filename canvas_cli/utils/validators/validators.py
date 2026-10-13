from jsonschema import ValidationError, validators

from canvas_cli.utils.context import context
from canvas_cli.utils.print import print
from canvas_cli.utils.validators.manifest_schema import manifest_schema


def get_default_host(host: str | None) -> str | None:
    """Return context's default host if the host param is null."""
    return host or context.default_host


def _lookup(name: str) -> str:
    """How Canvas Platform matches a pricing unit or vendor: case and spacing ignored."""
    return " ".join(name.split()).lower()


def _refuse_repeated_names(catalog: object) -> None:
    """Refuse a catalog block naming a pricing unit or vendor twice.

    JSON Schema compares whole items, so it cannot see `Visit` and `visit` as one unit;
    Canvas Platform refuses the push, so validation refuses it first.
    """
    if not isinstance(catalog, dict):
        return
    for key, field, what in (("pricing", "unit", "unit"), ("vendors", "name", "vendor")):
        names = [
            _lookup(item[field])
            for item in catalog.get(key) or []
            if isinstance(item, dict) and isinstance(item.get(field), str)
        ]
        if len(set(names)) != len(names):
            raise ValidationError(f"catalog {key} names a {what} twice.")


def validate_manifest_file(manifest_json: dict) -> None:
    """Validates a Canvas Manifest json against the manifest schema."""
    if "secrets" in manifest_json:
        print(
            "Warning: 'secrets' is deprecated. Use 'variables' instead, e.g.:\n"
            '  "variables": [{"name": "MY_KEY", "sensitive": true}]'
        )

    validator = validators.validator_for(manifest_schema)(manifest_schema)
    tag_warnings = []
    tag_value_warnings = []
    other_warnings = []
    for error in validator.iter_errors(manifest_json):
        if error.path and len(error.path) and error.path[0] == "tags":
            if error.validator == "enum":
                tag_value_warnings.append(error)
            elif error.validator == "additionalProperties":
                tag_warnings.append(error)
            else:
                other_warnings.append(error)
        else:
            raise error

    _refuse_repeated_names(manifest_json.get("catalog"))

    if tag_warnings:
        print("Warning: there are unrecognized tags in the manifest file:")
        for tag_warning in tag_warnings:
            print(f"\t- {tag_warning.message}")
    if tag_value_warnings:
        print("Warning: there are unrecognized tag values in the manifest file:")
        for tag_value_warning in tag_value_warnings:
            tag_category = tag_value_warning.path[1]
            print(
                f"\t- Please choose a valid tag value for '{tag_category}'. {tag_value_warning.message}."
            )
