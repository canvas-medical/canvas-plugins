import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class PracticeLocationSetting(TrackableFieldsModel):
    """
    Effect to upsert a PracticeLocationSetting row (per-location runtime config).

    Example:
        PracticeLocationSetting(
            practice_location_id="<uuid>",
            name="printed_prescription_format",
            value={"format": "letter"},
        ).upsert()
    """

    class Meta:
        effect_type = "PRACTICE_LOCATION_SETTING"

    practice_location_id: str | UUID | None = None
    name: str | None = None
    value: Any | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "upsert":
            for required in ("practice_location_id", "name"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to upsert a practice location setting.",
                            getattr(self, required),
                        )
                    )
        return errors

    def upsert(self) -> Effect:
        """Upsert (insert or update) a Practice Location Setting."""
        self._validate_before_effect("upsert")
        return Effect(
            type=f"UPSERT_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("PracticeLocationSetting",)
