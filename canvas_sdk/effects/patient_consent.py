"""Record a patient's decision on a consent, and optionally file the signed document."""

import base64
import binascii
import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.patient_consent import (
    PatientConsentCoding,
    PatientConsentRejectionCoding,
    PatientConsentStatus,
)

REJECTED_STATES = (PatientConsentStatus.REJECTED, PatientConsentStatus.REJECTED_VIA_PORTAL)


class ConsentCodingReference(BaseModel):
    """Identifies a coding by system and code, or by system and display when the code is empty."""

    system: str
    code: str = ""
    display: str = ""

    @model_validator(mode="after")
    def _has_code_or_display(self) -> "ConsentCodingReference":
        if not self.code and not self.display:
            raise ValueError("A coding reference needs a code or a display.")
        return self

    def lookup(self) -> dict[str, str]:
        """The filter that finds the coding: the code when present, else the display."""
        if self.code:
            return {"system": self.system, "code": self.code}
        return {"system": self.system, "display": self.display}


class ConsentDocument(BaseModel):
    """A signed consent document. The content is the file bytes, base64 encoded."""

    # Canvas stores the document under this name in a 255-character file field.
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

    @field_validator("filename")
    @classmethod
    def _is_plain_name(cls, filename: str) -> str:
        if "/" in filename or "\\" in filename or filename in (".", ".."):
            raise ValueError("The filename must be a plain file name, with no path.")
        return filename


class RecordPatientConsent(_BaseEffect):
    """Record a patient's decision on one consent.

    Each patient has one consent record per consent coding. The first decision creates it, and
    a later decision updates it. A document is added to the consent's document stack with
    effective_date as its date. The document with the latest date is the active document, and
    earlier signed copies stay on the chart.

    Canvas computes the expiration date from the coding's expiration rule. An accepted state
    clears any earlier rejection reason. The effect changes only the named consent, so a consent
    the patient did not answer stays pending.

    The fields are strictly typed: state takes a PatientConsentStatus member, not a string, and
    effective_date takes a datetime.date, not a datetime.

    Example:
        RecordPatientConsent(
            patient_id=patient.id,
            consent=ConsentCodingReference(system="INTERNAL", code="TELEHEALTH"),
            state=PatientConsentStatus.ACCEPTED_VIA_PORTAL,
            effective_date=datetime.date.today(),
            document=ConsentDocument(filename="telehealth.pdf", content=pdf_base64),
        ).apply()
    """

    class Meta:
        effect_type = EffectType.RECORD_PATIENT_CONSENT
        apply_required_fields = ("patient_id", "consent", "state", "effective_date")

    patient_id: str | None = None
    consent: ConsentCodingReference | None = None
    state: PatientConsentStatus | None = None
    effective_date: datetime.date | None = None
    rejection_reason: ConsentCodingReference | None = None
    document: ConsentDocument | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.patient_id and not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value", f"Patient with ID {self.patient_id} does not exist.", self.patient_id
                )
            )

        if self.consent:
            errors.extend(self._coding_errors(PatientConsentCoding, self.consent, "consent"))

        if self.rejection_reason:
            if self.state not in REJECTED_STATES:
                errors.append(
                    self._create_error_detail(
                        "value", "Set rejection_reason only with a rejected state.", self.state
                    )
                )
            else:
                errors.extend(
                    self._coding_errors(
                        PatientConsentRejectionCoding, self.rejection_reason, "rejection"
                    )
                )

        if self.document:
            try:
                # Line breaks are allowed, as base64.encodebytes() writes them.
                base64.b64decode("".join(self.document.content.split()), validate=True)
            except binascii.Error:
                errors.append(
                    self._create_error_detail(
                        "value", "The document content must be base64 encoded.", None
                    )
                )

        return errors

    def _coding_errors(
        self,
        model: type[PatientConsentCoding] | type[PatientConsentRejectionCoding],
        reference: ConsentCodingReference,
        label: str,
    ) -> list[InitErrorDetails]:
        """Require the reference to match exactly one coding."""
        matches = model.objects.filter(**reference.lookup()).count()
        if matches == 1:
            return []
        message = (
            f"The {label} coding does not exist."
            if matches == 0
            else f"The {label} coding reference matches more than one coding. Add a code."
        )
        return [self._create_error_detail("value", message, reference.lookup())]

    @property
    def values(self) -> dict[str, Any]:
        """The payload. apply() validates the required fields before it reads this."""
        assert self.consent and self.state and self.effective_date
        return {
            "patient_id": self.patient_id,
            "consent": self.consent.model_dump(),
            "state": self.state.value,
            "effective_date": self.effective_date.isoformat(),
            "rejection_reason": (
                self.rejection_reason.model_dump() if self.rejection_reason else None
            ),
            "document": self.document.model_dump() if self.document else None,
        }


__exports__ = ("ConsentCodingReference", "ConsentDocument", "RecordPatientConsent")
