"""Field checks shared by the effects that write records holding plugin uploads."""

from collections.abc import Iterable
from typing import Any

from django.db.models import Manager, QuerySet
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel


def upload_key_errors(model: TrackableFieldsModel, field: str) -> list[InitErrorDetails]:
    """Return an error for each value of ``field`` that is not a plugin upload key.

    A field that was set must hold the ``key`` of a file uploaded through a SimpleAPI route
    declared with ``file_uploads="stored"``, or a list of them. Canvas checks that each key
    belongs to the calling plugin when the effect is applied.
    """
    if not model.is_dirty(field):
        return []
    value = getattr(model, field)
    keys = value if isinstance(value, list) else [value]
    return [
        model._create_error_detail(
            "value",
            f"Field '{field}' must be the key of a file uploaded through a SimpleAPI route "
            "declared with file_uploads='stored'.",
            key,
        )
        for key in keys
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
    model: TrackableFieldsModel,
    field: str,
    records: Manager[Any] | QuerySet[Any],
    record: str,
    action: str,
) -> list[InitErrorDetails]:
    """Return an error when ``field`` is unset or names no row of ``records``."""
    value = getattr(model, field)
    if value is None:
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
