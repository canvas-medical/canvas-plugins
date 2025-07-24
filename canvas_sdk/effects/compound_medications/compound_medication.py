import json
from typing import Any

from pydantic_core import InitErrorDetails, PydanticCustomError

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
        return super().values

    @staticmethod
    def process_formulation(formulation: str | None) -> str | None:
        """
        Process compound medication formulation by stripping whitespace.

        Args:
            formulation: The formulation string to process

        Returns:
            Processed formulation string, or None if input was None
        """
        if formulation is None:
            return None
        return formulation.strip()

    @staticmethod
    def process_ndc(ndc: str | None) -> str | None:
        """
        Process compound medication NDC by removing dashes.

        Args:
            ndc: The NDC string to process

        Returns:
            Processed NDC string with dashes removed, or None if input was None
        """
        if ndc is None:
            return None
        return ndc.replace("-", "")

    @staticmethod
    def process_compound_medication_data(data: dict[str, Any]) -> dict[str, Any]:
        """
        Process compound medication data by applying all necessary transformations.

        Args:
            data: Dictionary containing compound medication data

        Returns:
            Processed dictionary with transformations applied
        """
        processed_data = data.copy()

        # Process formulation
        if "formulation" in processed_data and processed_data["formulation"] is not None:
            processed_data["formulation"] = CompoundMedication.process_formulation(
                processed_data["formulation"]
            )

        # Process NDC
        if (
            "controlled_substance_ndc" in processed_data
            and processed_data["controlled_substance_ndc"] is not None
        ):
            processed_data["controlled_substance_ndc"] = CompoundMedication.process_ndc(
                processed_data["controlled_substance_ndc"]
            )

        return processed_data

    @staticmethod
    def validate_compound_medication_fields(
        formulation: str | None,
        potency_unit_code: str | None,
        controlled_substance: str | None,
        controlled_substance_ndc: str | None,
    ) -> list[InitErrorDetails]:
        """
        Static method to validate compound medication fields.

        Args:
            formulation: The formulation value to validate
            potency_unit_code: The potency unit code to validate
            controlled_substance: The controlled substance to validate
            controlled_substance_ndc: The NDC to validate

        Returns:
            List of InitErrorDetails for any validation errors
        """

        def create_error(error_type: str, message: str, value: Any) -> InitErrorDetails:
            """Helper function to mimic _create_error_details."""
            return InitErrorDetails(
                {"type": PydanticCustomError(error_type, message), "input": value}
            )

        errors = []

        # Formulation validation
        if formulation is not None:
            stripped_formulation = formulation.strip()
            if not stripped_formulation:
                errors.append(
                    create_error(
                        "value",
                        "Field 'formulation' cannot be empty.",
                        formulation,
                    )
                )
            elif len(stripped_formulation) > 105:
                errors.append(
                    create_error(
                        "value",
                        "Field 'formulation' must be 105 characters or less.",
                        formulation,
                    )
                )

        # Potency unit code validation
        if potency_unit_code and potency_unit_code not in [
            choice[0] for choice in CompoundMedicationModel.PotencyUnits.choices
        ]:
            errors.append(
                create_error(
                    "value",
                    f"Invalid potency unit code: {potency_unit_code}. Must be one of: {[choice[0] for choice in CompoundMedicationModel.PotencyUnits.choices]}",
                    potency_unit_code,
                )
            )

        # Controlled substance validation
        if controlled_substance and controlled_substance not in [
            choice[0] for choice in CompoundMedicationModel.ControlledSubstanceOptions.choices
        ]:
            errors.append(
                create_error(
                    "value",
                    f"Invalid controlled substance: {controlled_substance}. Must be one of: {[choice[0] for choice in CompoundMedicationModel.ControlledSubstanceOptions.choices]}",
                    controlled_substance,
                )
            )

        # NDC validation - required when controlled substance is not "N" (Not Scheduled)
        if (
            controlled_substance
            and controlled_substance
            != CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED.value
            and (not controlled_substance_ndc or not controlled_substance_ndc.strip())
        ):
            errors.append(
                create_error(
                    "value",
                    "NDC is required when a Controlled Substance is specified.",
                    controlled_substance_ndc,
                )
            )

        return errors

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

        compound_med_errors = self.validate_compound_medication_fields(
            formulation=self.formulation,
            potency_unit_code=self.potency_unit_code,
            controlled_substance=self.controlled_substance,
            controlled_substance_ndc=self.controlled_substance_ndc,
        )
        errors.extend(compound_med_errors)

        return errors

    def create(self) -> Effect:
        """Create a new Compound Medication."""
        self._validate_before_effect("create")

        # Get raw values and apply explicit processing
        raw_data = self.values
        processed_data = self.process_compound_medication_data(raw_data)

        payload = {"data": processed_data}
        if self.active is None:
            payload["data"]["active"] = True

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )

    def update(self) -> Effect:
        """Update an existing Compound Medication."""
        self._validate_before_effect("update")

        # Get raw values and apply explicit processing
        raw_data = self.values
        processed_data = self.process_compound_medication_data(raw_data)

        payload = {"data": processed_data}
        payload["data"]["instance_id"] = str(self.instance_id)

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )


__exports__ = ("CompoundMedication",)
