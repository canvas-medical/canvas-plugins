import re
from pathlib import PurePosixPath

from jsonschema import ValidationError, validators
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from canvas_cli.utils.context import context
from canvas_cli.utils.print import print
from canvas_cli.utils.validators.manifest_schema import BUNDLE_FORBIDDEN_KEYS, manifest_schema

# A remote git repository: an https or ssh URL, or an scp-style address (git@host:path).
GIT_REMOTE = re.compile(r"^(?:(?:https|ssh)://[^\s/]+/\S+|[\w.-]+@[\w.-]+:\S+)$")


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


def _refuse_bad_dependencies(manifest_json: dict) -> None:
    """Refuse a dependency with an unparsable version, named twice, or naming the plugin itself.

    JSON Schema checks each entry's shape; these rules span entries or need PEP 440 parsing.
    """
    seen: set[tuple[str, str | None]] = set()
    for dependency in manifest_json.get("dependencies") or []:
        name, version = dependency["name"], dependency["version"]
        try:
            Version(version)
        except InvalidVersion:
            try:
                SpecifierSet(version)
            except InvalidSpecifier:
                raise ValidationError(
                    f"dependency {name!r}: {version!r} is neither a version nor a version specifier."
                ) from None
        if name == manifest_json.get("name"):
            raise ValidationError(f"dependency {name!r} is the plugin itself.")
        key = (name, dependency.get("publisher"))
        if key in seen:
            raise ValidationError(f"dependency {name!r} is named twice.")
        seen.add(key)
        if "source" in dependency:
            _refuse_bad_source(name, dependency["source"])


def _refuse_bad_source(name: str, source: dict) -> None:
    """Refuse a source that is not a remote git repository, or whose path leaves it."""
    if not GIT_REMOTE.match(source["git"]):
        raise ValidationError(
            f"dependency {name!r}: source git must be an https:// or ssh:// repository URL, "
            "or an scp-style address such as git@github.com:org/repo."
        )
    path = PurePosixPath(source.get("path", "."))
    if path.is_absolute() or ".." in path.parts:
        raise ValidationError(
            f"dependency {name!r}: source path must be a folder inside the repository."
        )


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
        # The only false schemas are the keys a bundle may not carry, and jsonschema
        # reports those without naming the key, so the message names them itself.
        if error.schema is False:
            carried = ", ".join(key for key in BUNDLE_FORBIDDEN_KEYS if key in manifest_json)
            raise ValidationError(
                f"A bundle carries no code of its own, so it cannot declare {carried}."
            )
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
    _refuse_bad_dependencies(manifest_json)

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
