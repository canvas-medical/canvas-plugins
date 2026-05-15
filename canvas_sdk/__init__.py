import os
import sys
from typing import Any

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if "mypy" not in sys.argv[0]:
    import django

    django.setup()

    from django.db import models

    from canvas_sdk.v1.data.base import (
        MAX_BULK_SIZE,
        BulkOperationTooLarge,
        _check_write_permission,
    )

    # --- raw: block entirely ---
    def _raw_blocked(*args: Any, **kwargs: Any) -> None:
        """Use of `raw` is forbidden."""
        raise PermissionError("raw() queries are not allowed")

    models.Manager.raw = _raw_blocked  # type: ignore[assignment, method-assign]

    # --- bulk_create ---
    _original_bulk_create = models.QuerySet.bulk_create

    def _wrapped_bulk_create(self: Any, objs: Any, *args: Any, **kwargs: Any) -> Any:
        """Wrapper that adds write-permission, size, and field-size checks."""
        _check_write_permission()
        objs = list(objs)
        if len(objs) > MAX_BULK_SIZE:
            raise BulkOperationTooLarge(
                f"bulk_create() received {len(objs):,} objects, "
                f"exceeding the {MAX_BULK_SIZE:,} limit."
            )
        for obj in objs:
            if hasattr(obj, "_check_field_sizes"):
                obj._check_field_sizes()
        return _original_bulk_create(self, objs, *args, **kwargs)

    models.QuerySet.bulk_create = _wrapped_bulk_create  # type: ignore[method-assign]

    # --- bulk_update ---
    _original_bulk_update = models.QuerySet.bulk_update

    def _wrapped_bulk_update(self: Any, objs: Any, *args: Any, **kwargs: Any) -> Any:
        """Wrapper that adds write-permission, size, and field-size checks."""
        _check_write_permission()
        objs = list(objs)
        if len(objs) > MAX_BULK_SIZE:
            raise BulkOperationTooLarge(
                f"bulk_update() received {len(objs):,} objects, "
                f"exceeding the {MAX_BULK_SIZE:,} limit."
            )
        for obj in objs:
            if hasattr(obj, "_check_field_sizes"):
                obj._check_field_sizes()
        return _original_bulk_update(self, objs, *args, **kwargs)

    models.QuerySet.bulk_update = _wrapped_bulk_update  # type: ignore[method-assign]

    # --- QuerySet.delete ---
    _original_qs_delete = models.QuerySet.delete

    def _wrapped_qs_delete(self: Any) -> tuple[int, dict[str, int]]:
        """Wrapper that adds a write-permission check."""
        _check_write_permission()
        return _original_qs_delete(self)

    models.QuerySet.delete = _wrapped_qs_delete  # type: ignore[method-assign]

    # --- QuerySet.update ---
    _original_qs_update = models.QuerySet.update

    def _wrapped_qs_update(self: Any, **kwargs: Any) -> int:
        """Wrapper that adds a write-permission check."""
        _check_write_permission()
        return _original_qs_update(self, **kwargs)

    models.QuerySet.update = _wrapped_qs_update  # type: ignore[method-assign]


__exports__ = ()
