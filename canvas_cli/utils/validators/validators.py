from jsonschema import ValidationError, validators
from packaging.specifiers import InvalidSpecifier, Specifier
from packaging.version import InvalidVersion, Version

from canvas_cli.utils.context import context
from canvas_cli.utils.print import print
from canvas_cli.utils.validators.manifest_schema import BUNDLE_FORBIDDEN_KEYS, manifest_schema


def get_default_host(host: str | None) -> str | None:
    """Return context's default host if the host param is null."""
    return host or context.default_host


def _lookup(name: str) -> str:
    """How Canvas Platform matches a pricing unit or vendor: case and spacing ignored."""
    return " ".join(name.split()).lower()


def _refuse_repeated_names(catalog: object) -> None:
    """Refuse a catalog block naming a pricing unit or vendor twice, or a fractional markup.

    JSON Schema compares whole items, so it cannot see `Visit` and `visit` as one unit, and
    its integer takes `1500.0`; Canvas Platform refuses the push, so validation refuses it first.
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
    for item in catalog.get("pricing") or []:
        # JSON Schema's integer takes 1500.0; Canvas Platform takes only a whole int.
        if isinstance(item, dict) and isinstance(item.get("markup_bps"), float):
            raise ValidationError("markup_bps is a whole number such as 1500, not 1500.0.")


def normalized_version(version: str) -> str | None:
    """The PEP 440 normal form of ``version`` as one exact version, or None when it is not one.

    ``1.16.0`` is its own normal form, while ``v1.16.0`` and `` 1.16.0`` parse to ``1.16.0``
    without being written that way.
    """
    try:
        return str(Version(version))
    except InvalidVersion:
        return None


def is_dependency_version(version: str) -> bool:
    """Whether ``version`` is a pin a dependency accepts.

    That is one exact PEP 440 version in its normal form, such as ``1.16.0``, or a
    compatible release with at least two release components, such as ``~=1.16`` or
    ``~=0.1.1``.
    """
    if (normalized := normalized_version(version)) is not None:
        return normalized == version
    try:
        specifier = Specifier(version)
    except InvalidSpecifier:
        return False
    return specifier.operator == "~=" and str(specifier) == version


def _refuse_bad_dependencies(manifest_json: dict) -> None:
    """Refuse a dependency whose version is not a pin, named twice, or naming the plugin itself.

    A dependency is the plugin itself when it carries the plugin's name and the manifest
    names no ``publisher`` or the same one; the same name from another publisher is
    another plugin.

    JSON Schema checks each entry's shape; these rules span entries or need PEP 440 parsing.
    """
    seen: set[tuple[str, str]] = set()
    for dependency in manifest_json.get("dependencies") or []:
        name, publisher, version = (
            dependency["name"],
            dependency["publisher"],
            dependency["version"],
        )
        normalized = normalized_version(version)
        if normalized is not None and normalized != version:
            raise ValidationError(
                f"dependency {name!r}: {version!r} is not written as an exact version; "
                f"write it as {normalized!r}."
            )
        if not is_dependency_version(version):
            raise ValidationError(
                f"dependency {name!r}: {version!r} is not a version a dependency accepts. "
                "Name one exact version, such as '1.16.0', or a compatible release, such as "
                "'~=1.16' (1.16 or later, below 2.0) or '~=0.1.1' (0.1.1 or later, below 0.2)."
            )
        if name == manifest_json.get("name") and manifest_json.get("publisher") in (
            None,
            publisher,
        ):
            raise ValidationError(f"dependency {name!r} is the plugin itself.")
        if (name, publisher) in seen:
            raise ValidationError(f"dependency {name!r} of {publisher!r} is named twice.")
        seen.add((name, publisher))


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
        # A dependency's name follows the plugin name rule; Canvas Platform refuses it with
        # this sentence, so the CLI does too.
        if (
            len(error.path) == 3
            and error.path[0] == "dependencies"
            and error.path[2] == "name"
            and error.validator in ("pattern", "maxLength")
        ):
            raise ValidationError(
                f"dependency name {error.instance!r} must be lowercase letters, digits and "
                "underscores, starting with a letter, at most 256 characters."
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
