from jsonschema import validators

from canvas_cli.utils.context import context
from canvas_cli.utils.print import print
from canvas_cli.utils.validators.manifest_schema import manifest_schema


def get_default_host(host: str | None) -> str | None:
    """Return context's default host if the host param is null."""
    return host or context.default_host


def validate_manifest_file(manifest_json: dict) -> None:
    """Validates a Canvas Manifest json against the manifest schema."""
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
