from enum import Enum
from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PanelConfiguration(_BaseEffect):
    """
    An Effect that will decide which buttons appear on the panel section in Canvas.
    """

    class Meta:
        effect_type = EffectType.SHOW_PANEL_SECTIONS

    class Context(Enum):
        GLOBAL = "global"
        PATIENT = "patient"

    class PanelGlobalSection(Enum):
        APPOINTMENT = "appointment"
        CHANGE_REQUEST = "changeRequest"
        IMAGING_REPORT = "imagingReport"
        INPATIENT_STAY = "inpatientStay"
        LAB_REPORT = "labReport"
        MESSAGE = "message"
        OUTSTANDING_REFERRAL = "outstandingReferral"
        PRESCRIPTION_ALERT = "prescriptionAlert"
        RECALL_APPOINTMENT = "recallAppointment"
        REFERRAL_REPORT = "referralReport"
        REFILL_REQUEST = "refillRequest"
        TASK = "task"
        UNCATEGORIZED_DOCUMENT = "uncategorizedDocument"

    class PanelPatientSection(Enum):
        CHANGE_REQUEST = "changeRequest"
        COMMAND = "command"
        LAB_REPORT = "labReport"
        IMAGING_REPORT = "imagingReport"
        INPATIENT_STAY = "inpatientStay"
        PRESCRIPTION_ALERT = "prescriptionAlert"
        REFERRAL_REPORT = "referralReport"
        REFILL_REQUEST = "refillRequest"
        TASK = "task"
        UNCATEGORIZED_DOCUMENT = "uncategorizedDocument"

    sections: list[PanelPatientSection] | list[PanelGlobalSection] = Field(min_length=1)
    context: Context

    @property
    def values(self) -> dict[str, Any]:
        """The PanelConfiguration's values."""
        return {"sections": [s.value for s in self.sections]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.context == self.Context.GLOBAL and not all(
            isinstance(s, self.PanelGlobalSection) for s in self.sections
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    "All sections must be of type PanelGlobalSection",
                    self.sections,
                )
            )

        if self.context == self.Context.PATIENT and not all(
            isinstance(s, self.PanelPatientSection) for s in self.sections
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    "All sections must be of type PanelPatientSection",
                    self.sections,
                )
            )

        return errors


__exports__ = ("PanelConfiguration",)
