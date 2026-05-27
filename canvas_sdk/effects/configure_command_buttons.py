from enum import StrEnum
from typing import Any

from pydantic import ConfigDict
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class ConfigureCommandButtons(_BaseEffect):
    """
    An Effect that configures the visibility of command buttons in patient chart locations.

    Locations not listed retain their default visible/enabled state.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    class Meta:
        effect_type = EffectType.PATIENT_CHART__CONFIGURE_COMMAND_BUTTONS

    class Location(StrEnum):
        SOCIAL_DETERMINANTS = "social_determinants"
        GOALS = "goals"
        CONDITIONS = "conditions"
        MEDICATIONS = "medications"
        ALLERGIES = "allergies"
        CARE_TEAMS = "care_teams"
        VITALS = "vitals"
        IMMUNIZATIONS = "immunizations"
        SURGICAL_HISTORY = "surgical_history"
        FAMILY_HISTORY = "family_history"
        CODING_GAPS = "coding_gaps"
        QUALITY_PROTOCOLS = "quality_protocols"
        LAB_REVIEWS = "lab_reviews"
        IMAGING_REVIEWS = "imaging_reviews"
        REFERRAL_REVIEWS = "referral_reviews"
        DOCUMENT_REVIEWS = "document_reviews"

    class Visibility(StrEnum):
        VISIBLE = "visible"
        HIDDEN = "hidden"
        DISABLED = "disabled"

    class LocationConfig:
        """Configuration for a single command button location."""

        def __init__(
            self,
            location: "ConfigureCommandButtons.Location",
            visibility: "ConfigureCommandButtons.Visibility",
        ) -> None:
            """Initialize a LocationConfig."""
            self.location = location
            self.visibility = visibility

        def to_dict(self) -> dict[str, Any]:
            """Convert to a dictionary."""
            return {"location": self.location, "visibility": self.visibility}

    patient_id: str
    locations: list[LocationConfig] = []

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate that no location appears more than once."""
        error_details = super()._get_error_details(method)
        seen: set = set()
        for config in self.locations:
            if config.location in seen:
                error_details.append(
                    self._create_error_detail(
                        "value",
                        f"Duplicate location in ConfigureCommandButtons: {config.location.value!r}",
                        config.location.value,
                    )
                )
            seen.add(config.location)
        return error_details

    @property
    def values(self) -> dict[str, Any]:
        """The location visibility configuration."""
        return {
            "patient_id": self.patient_id,
            "locations": [config.to_dict() for config in self.locations],
        }


__exports__ = ("ConfigureCommandButtons",)
