import json
from enum import StrEnum
from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class SetupCompletionStatus(StrEnum):
    """Lifecycle status for an instance-config setup section."""

    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class SetupCompletion(TrackableFieldsModel):
    """
    Effect to record progress on an instance-config setup section (one of
    Organization, Branding, Practice Locations, Roles, Staff, Note Types,
    Insurers, Settings — the checklist on the /set-up/ dashboard).

    Plugins can upsert a row to mark a section completed or skipped, which
    drives the dashboard progress bar and the "auto-switch to Edit Mode"
    behavior described in the Notion handoff bundle.
    """

    class Meta:
        effect_type = "SETUP_COMPLETION"

    section_id: str | None = None
    status: SetupCompletionStatus | None = Field(default=None, strict=False)

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "upsert":
            for required in ("section_id", "status"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to upsert setup completion.",
                            getattr(self, required),
                        )
                    )
        return errors

    def upsert(self) -> Effect:
        """Upsert a setup completion row."""
        self._validate_before_effect("upsert")
        return Effect(
            type=f"UPSERT_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("SetupCompletion", "SetupCompletionStatus")
