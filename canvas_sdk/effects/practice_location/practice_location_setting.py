import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class PracticeLocationSettingName(StrEnum):
    """Per-location settings a plugin may set."""

    LAB_REVIEW_EMAIL_SUBJECT = "labReviewEmailSubject"
    LAB_REVIEW_EMAIL_TEMPLATE = "labReviewEmailTemplate"
    LAB_REVIEW_TEXT_MESSAGE_TEMPLATE = "labReviewTextMessageTemplate"
    PREFERRED_LAB_PARTNER = "preferredLabPartner"
    PRINTED_PRESCRIPTION_FORMAT = "printedPrescriptionFormat"
    PROVIDER_MESSAGE_EMAIL_SUBJECT = "providerMessageEmailSubject"
    PROVIDER_MESSAGE_EMAIL_TEMPLATE = "providerMessageEmailTemplate"
    PROVIDER_MESSAGE_TEXT_MESSAGE_TEMPLATE = "providerMessageTextMessageTemplate"
    SCANNER_INTEGRATION = "scannerIntegration"
    SERVICE_AREA_ZIP_CODES = "serviceAreaZipCodes"


class PracticeLocationSetting(TrackableFieldsModel):
    """Create or replace one setting on a practice location.

    ``practice_location_id`` is the location's id.
    """

    class Meta:
        effect_type = "PRACTICE_LOCATION_SETTING"

    practice_location_id: str | UUID | None = None
    name: PracticeLocationSettingName | None = Field(default=None, strict=False)
    value: Any = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
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
        """Build the UPSERT effect."""
        self._validate_before_effect("upsert")
        return Effect(
            type=f"UPSERT_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("PracticeLocationSetting", "PracticeLocationSettingName")
