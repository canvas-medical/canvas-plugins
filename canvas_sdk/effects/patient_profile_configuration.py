from enum import Enum
from typing import Any

from pydantic import Field
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientProfileConfiguration(_BaseEffect):
    """
    An Effect that will decide which sections appear, and if they start expanded,
    on the patient's profile in Canvas.
    """

    class Meta:
        effect_type = EffectType.SHOW_PATIENT_PROFILE_SECTIONS

    class Section(Enum):
        DEMOGRAPHICS = "demographics"
        PORTAL = "portal"
        PREFERENCES = "preferences"
        PREFERRED_PHARMACIES = "preferred_pharmacies"
        PATIENT_CONSENTS = "patient_consents"
        CARE_TEAM = "care_team"
        PARENT_GUARDIAN = "parent_guardian"
        ADDRESSES = "addresses"
        TELECOM = "telecom"
        CONTACTS = "contacts"

    class Payload(TypedDict):
        type: "PatientProfileConfiguration.Section"
        start_expanded: bool

    sections: list[Payload] = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The PatientProfileConfiguration's values."""
        return {"sections": [{**s, "type": s["type"].value} for s in self.sections]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientProfileConfiguration",)
