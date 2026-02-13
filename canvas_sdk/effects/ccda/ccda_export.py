import xml.etree.ElementTree as ET
from enum import StrEnum
from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.v1.data import Patient
from logger import log


class DocumentType(StrEnum):
    """Valid CCDA document types."""

    CCD = "CCD"
    REFERRAL = "Referral"


class CreateCCDAExport(_BaseEffect):
    """
    An Effect that will create a CCDA document for a patient with the provided XML content.

    Attributes:
        patient_id: The patient's key (required)
        content: The CCDA XML content as a string (required)
        document_type: Type of CCDA document (default: DocumentType.CCD)
    """

    class Meta:
        effect_type = EffectType.CREATE_CCDA_EXPORT

    patient_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    document_type: DocumentType = Field(default=DocumentType.CCD, strict=False)

    @property
    def values(self) -> dict[str, Any]:
        """The CreateCCDAExport's values."""
        return {
            "patient_id": self.patient_id,
            "content": self.content,
            "document_type": self.document_type.value,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        log.info(f"Creating CCDA document for patient {self.patient_id}")
        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        # Validate XML content
        try:
            ET.fromstring(self.content)
        except ET.ParseError as e:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Invalid XML content: {e}",
                    self.content[:100] if len(self.content) > 100 else self.content,
                )
            )

        return errors


__exports__ = ("CreateCCDAExport", "DocumentType")
