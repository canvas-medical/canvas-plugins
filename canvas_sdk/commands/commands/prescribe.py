import json
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import Field, conlist
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import ClinicalQuantity
from canvas_sdk.effects import Effect
from canvas_sdk.effects.compound_medications.compound_medication import (
    CompoundMedication as CompoundMedicationEffect,
)
from canvas_sdk.v1.data.compound_medication import CompoundMedication as CompoundMedicationModel


class PrescribeCommand(_BaseCommand):
    """A class for managing a Prescribe command within a specific note."""

    class Meta:
        key = "prescribe"

    class Substitutions(Enum):
        ALLOWED = "allowed"
        NOT_ALLOWED = "not_allowed"

    fdb_code: str | None = Field(default=None, json_schema_extra={"commands_api_name": "prescribe"})
    icd10_codes: conlist(str, max_length=2) = Field(  # type: ignore[valid-type]
        default=[], json_schema_extra={"commands_api_name": "indications"}
    )
    sig: str = ""
    days_supply: int | None = None
    quantity_to_dispense: Decimal | float | int | None = None
    type_to_dispense: ClinicalQuantity | None = None
    refills: int | None = None
    substitutions: Substitutions | None = None
    pharmacy: str | None = None
    prescriber_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "prescriber"}
    )
    supervising_provider_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "supervising_provider"}
    )
    note_to_pharmacist: str | None = None

    # Compound medication fields
    compound_medication_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "compound_medication_id"}
    )
    compound_medication_formulation: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "compound_medication_formulation"}
    )
    compound_medication_potency_unit_code: str | None = Field(
        default=None,
        json_schema_extra={"commands_api_name": "compound_medication_potency_unit_code"},
    )
    compound_medication_controlled_substance: str | None = Field(
        default=None,
        json_schema_extra={"commands_api_name": "compound_medication_controlled_substance"},
    )
    compound_medication_controlled_substance_ndc: str | None = Field(
        default=None,
        json_schema_extra={"commands_api_name": "compound_medication_controlled_substance_ndc"},
    )
    compound_medication_active: bool | None = Field(
        default=None, json_schema_extra={"commands_api_name": "compound_medication_active"}
    )

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        """Add compound medication validation to the base validation."""
        errors = super()._get_error_details(method)

        # Validate that exactly one medication type is provided
        if method == "originate":
            has_fdb_code = self.fdb_code is not None and self.fdb_code.strip() != ""
            has_compound_medication_id = (
                self.compound_medication_id is not None
                and self.compound_medication_id.strip() != ""
            )
            has_compound_medication_formulation = (
                self.compound_medication_formulation is not None
                and self.compound_medication_formulation.strip() != ""
            )

            medication_types_provided = sum(
                [has_fdb_code, has_compound_medication_id, has_compound_medication_formulation]
            )

            if medication_types_provided == 0:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Must provide one of: 'fdb_code', 'compound_medication_id', or 'compound_medication_formulation' to prescribe a medication.",
                        None,
                    )
                )
            elif medication_types_provided > 1:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Cannot specify multiple medication types. Choose one of: 'fdb_code', 'compound_medication_id', or 'compound_medication_formulation'.",
                        None,
                    )
                )

        # Validate compound medication ID if provided
        if (
            self.compound_medication_id
            and self.compound_medication_id.strip() != ""
            and
            # Check if compound medication exists
            not CompoundMedicationModel.objects.filter(id=self.compound_medication_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Compound medication with ID {self.compound_medication_id} does not exist.",
                    self.compound_medication_id,
                )
            )

        # Use static validation method for compound medication fields
        if self.compound_medication_formulation is not None:
            compound_med_errors = CompoundMedicationEffect.validate_compound_medication_fields(
                formulation=self.compound_medication_formulation,
                potency_unit_code=self.compound_medication_potency_unit_code,
                controlled_substance=self.compound_medication_controlled_substance,
                controlled_substance_ndc=self.compound_medication_controlled_substance_ndc,
            )
            errors.extend(compound_med_errors)

        return errors

    def _process_compound_medication_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process compound medication fields in prescription data.

        Args:
            data: Dictionary containing prescription data

        Returns:
            Processed dictionary with compound medication transformations applied
        """
        # Process nested compound medication values if present
        if "compound_medication_values" in data:
            compound_med_data = data["compound_medication_values"]
            processed_compound_data = CompoundMedicationEffect.process_compound_medication_data(
                compound_med_data
            )
            data["compound_medication_values"] = processed_compound_data

        return data

    @property
    def values(self) -> dict:
        """The Prescribe command's field values."""
        values = super().values

        if self.is_dirty("quantity_to_dispense"):
            values["quantity_to_dispense"] = (
                str(Decimal(self.quantity_to_dispense)) if self.quantity_to_dispense else None
            )

        # Group compound medication fields under a single key
        compound_medication_values = {}

        if "compound_medication_id" in values:
            compound_medication_values["id"] = values.pop("compound_medication_id")
        if "compound_medication_formulation" in values:
            compound_medication_values["formulation"] = values.pop(
                "compound_medication_formulation"
            )
        if "compound_medication_potency_unit_code" in values:
            compound_medication_values["potency_unit_code"] = values.pop(
                "compound_medication_potency_unit_code"
            )
        if "compound_medication_controlled_substance" in values:
            compound_medication_values["controlled_substance"] = values.pop(
                "compound_medication_controlled_substance"
            )
        if "compound_medication_controlled_substance_ndc" in values:
            compound_medication_values["controlled_substance_ndc"] = values.pop(
                "compound_medication_controlled_substance_ndc"
            )
        if "compound_medication_active" in values:
            compound_medication_values["active"] = values.pop("compound_medication_active")

        if compound_medication_values:
            values["compound_medication_values"] = compound_medication_values

        return values

    def originate(self, line_number: int = -1) -> Effect:
        """Originate a new command in the note body with explicit compound medication processing."""
        self._validate_before_effect("originate")

        # Get raw values and apply explicit processing for compound medications
        raw_data = self.values
        processed_data = self._process_compound_medication_fields(raw_data)

        return Effect(
            type=f"ORIGINATE_{self.constantized_key()}_COMMAND",
            payload=json.dumps(
                {
                    "command": self.command_uuid,
                    "note": self.note_uuid,
                    "data": processed_data,
                    "line_number": line_number,
                }
            ),
        )

    def edit(self) -> Effect:
        """Edit the command with explicit compound medication processing."""
        self._validate_before_effect("edit")

        # Get raw values and apply explicit processing for compound medications
        raw_data = self.values
        processed_data = self._process_compound_medication_fields(raw_data)

        return Effect(
            type=f"EDIT_{self.constantized_key()}_COMMAND",
            payload=json.dumps(
                {
                    "command": self.command_uuid,
                    "data": processed_data,
                }
            ),
        )


__exports__ = (
    "PrescribeCommand",
    # Not defined here but used in a current plugin
    "ClinicalQuantity",
    "Decimal",
)
