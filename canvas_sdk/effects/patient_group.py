from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect
from canvas_sdk.effects.base import EffectType, _BaseEffect, async_effect
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.patient_group import PatientGroup as PatientGroupModel


class PatientGroupEffect(Model):
    """
    Effect for performing actions on a Patient Group.

    Attributes:
        group_id (UUID | str): The unique identifier for the patient group instance.
    """

    group_id: UUID | str

    @async_effect
    def add_member(self, patient_ids: list[str]) -> Effect:
        """Add patient(s) as members of the group."""
        return _AddPatientGroupMember(group_id=self.group_id, patient_ids=patient_ids).apply()

    @async_effect
    def deactivate_member(self, patient_ids: list[str]) -> Effect:
        """Deactivate patient(s) from the group."""
        return _DeactivatePatientGroupMember(
            group_id=self.group_id, patient_ids=patient_ids
        ).apply()


class _PatientGroupBase(_BaseEffect):
    """Base class for managing Patient Groups."""

    group_id: UUID | str
    patient_ids: list[str]

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not PatientGroupModel.objects.filter(id=self.group_id).exists():
            errors.append(
                self._create_error_detail(
                    "group_id",
                    f"PatientGroup with id: {self.group_id} does not exist.",
                    self.group_id,
                )
            )

        if self.patient_ids:
            existing_ids = set(
                Patient.objects.filter(id__in=self.patient_ids).values_list("id", flat=True)
            )
            for patient_id in self.patient_ids:
                if patient_id not in existing_ids:
                    errors.append(
                        self._create_error_detail(
                            "patient_id",
                            f"Patient with id: {patient_id} does not exist.",
                            patient_id,
                        )
                    )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """The effect's serializable data."""
        return {"group_id": str(self.group_id), "patient_ids": self.patient_ids}


class _AddPatientGroupMember(_PatientGroupBase):
    """Effect to add a member to a Patient Group."""

    class Meta:
        effect_type = EffectType.PATIENT_GROUP__ADD_MEMBER


class _DeactivatePatientGroupMember(_PatientGroupBase):
    """Effect to deactivate a member from a Patient Group."""

    class Meta:
        effect_type = EffectType.PATIENT_GROUP__DEACTIVATE_MEMBER


__exports__ = ("PatientGroupEffect",)
