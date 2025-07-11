import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.v1.data.compound_medication import CompoundMedication as CompoundMedicationModel


class CompoundMedication(TrackableFieldsModel):
    """Effect to create or update a Compound Medication record."""

    class Meta:
        effect_type = "COMPOUND_MEDICATION"

    instance_id: str | None = None
    formulation: str | None = None
    potency_unit_code: str | None = None
    controlled_substance: str | None = None
    controlled_substance_ndc: str | None = None
    active: bool | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the compound medication as a dictionary, only including dirty (modified) fields."""
        values = super().values

        # Apply compound medication specific processing
        if "formulation" in values and values["formulation"] is not None:
            values["formulation"] = values["formulation"].strip()

        if "controlled_substance_ndc" in values and values["controlled_substance_ndc"] is not None:
            values["controlled_substance_ndc"] = values["controlled_substance_ndc"].replace("-", "")

        return values

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if not self.formulation:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'formulation' is required to create a compound medication.",
                        None,
                    )
                )

            if not self.potency_unit_code:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'potency_unit_code' is required to create a compound medication.",
                        None,
                    )
                )

            if not self.controlled_substance:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'controlled_substance' is required to create a compound medication.",
                        None,
                    )
                )

        elif method == "update":
            if not self.instance_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'instance_id' is required to update a compound medication.",
                        None,
                    )
                )

        if (
            self.instance_id
            and not CompoundMedicationModel.objects.filter(id=self.instance_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Compound medication with ID {self.instance_id} does not exist.",
                    self.instance_id,
                )
            )

        # Formulation validation
        if self.formulation is not None:
            stripped_formulation = self.formulation.strip()
            if not stripped_formulation:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'formulation' cannot be empty.",
                        self.formulation,
                    )
                )
            elif len(stripped_formulation) > 105:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'formulation' must be 105 characters or less.",
                        self.formulation,
                    )
                )

        # Potency unit code validation
        if self.potency_unit_code and self.potency_unit_code not in [
            choice[0] for choice in CompoundMedicationModel.PotencyUnits.choices
        ]:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Invalid potency unit code: {self.potency_unit_code}. Must be one of: {[choice[0] for choice in CompoundMedicationModel.PotencyUnits.choices]}",
                    self.potency_unit_code,
                )
            )

        # Controlled substance validation
        if self.controlled_substance and self.controlled_substance not in [
            choice[0] for choice in CompoundMedicationModel.ControlledSubstanceOptions.choices
        ]:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Invalid controlled substance: {self.controlled_substance}. Must be one of: {[choice[0] for choice in CompoundMedicationModel.ControlledSubstanceOptions.choices]}",
                    self.controlled_substance,
                )
            )

        # NDC validation - required when controlled substance is not "N" (Not Scheduled)
        if (
            self.controlled_substance
            and self.controlled_substance != "N"
            and (not self.controlled_substance_ndc or not self.controlled_substance_ndc.strip())
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    "NDC is required when a Controlled Substance is specified.",
                    self.controlled_substance_ndc,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a new Compound Medication."""
        self._validate_before_effect("create")

        payload = {"data": self.values}
        if self.active is None:
            payload["data"]["active"] = True

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )

    def update(self) -> Effect:
        """Update an existing Compound Medication."""
        self._validate_before_effect("update")

        payload = {"data": self.values}
        payload["data"]["instance_id"] = str(self.instance_id)

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )


__exports__ = ("CompoundMedication",)
