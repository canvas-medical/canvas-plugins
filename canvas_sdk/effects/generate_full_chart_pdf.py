from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.v1.data import Patient, Staff


class GenerateFullChartPDFEffect(_BaseEffect):
    """
    An Effect that will generate a full chart PDF for a patient.

    Generated PDF will appear in task list assigned to requestor with "chart pdf" label within 10 minutes.
    """

    class Meta:
        effect_type = EffectType.GENERATE_FULL_CHART_PDF

    patient_id: str = Field(min_length=1)
    requestor_staff_id: str = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The GenerateFullChartPDFEffect's values."""
        return {
            "patient_id": self.patient_id,
            "requestor_staff_id": self.requestor_staff_id,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        if not Staff.objects.filter(id=self.requestor_staff_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Requestor staff with ID {self.requestor_staff_id} does not exist.",
                    self.requestor_staff_id,
                )
            )

        return errors


__exports__ = ("GenerateFullChartPDFEffect",)
