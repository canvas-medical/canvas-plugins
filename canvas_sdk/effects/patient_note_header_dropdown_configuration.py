from enum import Enum
from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientNoteHeaderDropdownConfiguration(_BaseEffect):
    """
    An Effect that will decide which items appear on the patient note header dropdown.
    """

    class Meta:
        effect_type = EffectType.SHOW_PATIENT_NOTE_HEADER_DROPDOWN_SECTIONS

    class Items(Enum):
        LINK_TO_PHONE = "link_to_phone"
        SOAP = "soap"
        APSO = "apso"
        CHANGE_LOCATION = "change_location"
        CHANGE_PROVIDER = "change_provider"
        CHANGE_DATE_OF_SERVICE = "change_date_of_service"
        PRINT_SUPERBILL = "print_superbill"
        PRINT_ROOMING_SHEET = "print_rooming_sheet"
        PRINT_AFTER_VISIT_SUMMARY = "print_after_visit_summary"
        COPY_LINK = "copy_link"
        PRINT_NOTE = "print_note"
        FAX_NOTE = "fax_note"
        FAX_EVENT_HISTORY = "fax_event_history"
        MOVE_COMMANDS = "move_commands"

    items: list[Items] = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The PatientNoteHeaderDropdownConfiguration's values."""
        return {"items": [s.value for s in self.items]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientNoteHeaderDropdownConfiguration",)
