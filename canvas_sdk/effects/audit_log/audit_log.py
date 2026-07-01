import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class AuditAction(StrEnum):
    """Action verb stored on the ConfigAuditLog row."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditLog(TrackableFieldsModel):
    """
    Effect to write an entry to the ConfigAuditLog. Plugins call this when
    they perform a configuration change so the audit footer in /set-up/
    reflects "Last saved <date> by <plugin>" alongside human edits.
    """

    class Meta:
        effect_type = "AUDIT_LOG"

    section: str | None = None
    action: AuditAction | None = Field(default=None, strict=False)
    record_id: str | UUID | None = None
    changes: dict[str, Any] | None = None
    user_id: str | UUID | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "write":
            for required in ("section", "action"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to write an audit log entry.",
                            getattr(self, required),
                        )
                    )
        return errors

    def write(self) -> Effect:
        """Write an audit log entry."""
        self._validate_before_effect("write")
        return Effect(
            type=f"WRITE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("AuditLog", "AuditAction")
