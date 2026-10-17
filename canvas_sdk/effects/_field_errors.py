"""Field checks shared by the effects that write records holding plugin uploads."""

from collections.abc import Iterable
from typing import Any

from django.db.models import Manager, QuerySet
from pydantic_core import InitErrorDetails

from canvas_sdk.base import Model, TrackableFieldsModel


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def upload_key_errors(model: TrackableFieldsModel, *fields: str) -> list[InitErrorDetails]:
    """Return an error for each value of ``fields`` that is not a plugin upload key.

    A field that was set holds the ``key`` of a file uploaded through a SimpleAPI route
    declared with ``file_uploads="stored"``, or a list of them, or None for no file. Canvas
    checks that each key belongs to the calling plugin when the effect is applied.
    """
    return [
        model._create_error_detail(
            "value",
            f"Field '{field}' must be the key of a file uploaded through a SimpleAPI route "
            "declared with file_uploads='stored'.",
            key,
        )
        for field in fields
        if model.is_dirty(field)
        for key in _as_list(getattr(model, field))
        if not (key and (key.startswith("plugin-uploads/") or "/plugin-uploads/" in key))
    ]


def blank_field_errors(
    model: TrackableFieldsModel,
    fields: Iterable[str],
) -> list[InitErrorDetails]:
    """Return an error for each of ``fields`` that was set to None or an empty string."""
    return [
        model._create_error_detail(
            "value",
            f"Field '{field}' cannot be empty.",
            getattr(model, field),
        )
        for field in fields
        if model.is_dirty(field) and getattr(model, field) in (None, "")
    ]


def existing_record_errors(
    model: Model,
    field: str,
    records: Manager[Any] | QuerySet[Any],
    record: str,
    action: str | None = None,
) -> list[InitErrorDetails]:
    """Return an error when ``field`` names no row of ``records``.

    An unset ``field`` is an error only when ``action`` names what it is required for.
    """
    value = getattr(model, field)
    if value is None:
        if action is None:
            return []
        return [
            model._create_error_detail(
                "missing", f"Field '{field}' is required to {action} the {record}.", None
            )
        ]
    if not records.filter(**{"dbid" if isinstance(value, int) else "id": value}).exists():
        return [
            model._create_error_detail(
                "value",
                f"No {record} has id {value}.",
                value,
            )
        ]
    return []


__exports__ = ()
