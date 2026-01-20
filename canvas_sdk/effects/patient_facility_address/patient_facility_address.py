import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.v1.data.facility import Facility
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.patient import PatientFacilityAddress as PatientFacilityAddressModel


class AddressType(StrEnum):
    """Valid address types for PatientFacilityAddress."""

    PHYSICAL = "physical"
    BOTH = "both"


class PatientFacilityAddress(TrackableFieldsModel):
    """
    Effect to create, update, or delete a Patient Facility Address in Canvas.

    Patient facility addresses link patients to healthcare facilities with optional
    room number information. The address details (line1, line2, city, etc.) are
    automatically populated from the linked facility.

    You can either reference an existing facility by ID, or create a new facility
    inline by providing the facility details.

    Example (create with existing facility):
        effect = PatientFacilityAddress(
            patient_id="patient-uuid",
            facility_id="facility-uuid",
            room_number="101A",
            address_type="physical",
        )
        return effect.create()

    Example (create with new facility):
        effect = PatientFacilityAddress(
            patient_id="patient-uuid",
            facility_name="New Clinic",
            facility_line1="123 Main St",
            facility_city="Boston",
            facility_state_code="MA",
            facility_postal_code="02101",
            room_number="101A",
        )
        return effect.create()

    Example (update):
        effect = PatientFacilityAddress(
            id="existing-address-uuid",
            facility_id="new-facility-uuid",
            room_number="202B",
        )
        return effect.update()

    Example (delete):
        effect = PatientFacilityAddress(
            id="existing-address-uuid",
        )
        return effect.delete()
    """

    class Meta:
        effect_type = "PATIENT_FACILITY_ADDRESS"

    # For updates/delete - the externally_exposable_id
    id: str | UUID | None = None

    # For create - patient's UUID
    patient_id: str | UUID | None = None

    # Option 1: Reference existing facility
    facility_id: str | UUID | None = None

    # Option 2: Create new facility inline
    facility_name: str | None = None
    facility_npi_number: str | None = None
    facility_phone_number: str | None = None
    facility_fax_number: str | None = None
    facility_active: bool | None = None
    facility_line1: str | None = None
    facility_line2: str | None = None
    facility_city: str | None = None
    facility_district: str | None = None
    facility_state_code: str | None = None
    facility_postal_code: str | None = None

    # Address-specific fields
    room_number: str | None = None
    address_type: AddressType | None = Field(default=None, strict=False)

    def _has_facility_creation_fields(self) -> bool:
        """Check if any required facility creation fields are set."""
        return any(
            [
                self.facility_name is not None,
                self.facility_city is not None,
                self.facility_state_code is not None,
                self.facility_postal_code is not None,
            ]
        )

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the patient facility address data."""
        errors = super()._get_error_details(method)
        if method in ["create", "update"]:
            if method == "create":
                if self.id:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            "ID should not be set when creating a new patient facility address.",
                            self.id,
                        )
                    )
                if not self.patient_id:
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            "Field 'patient_id' is required to create a patient facility address.",
                            self.patient_id,
                        )
                    )
                elif not Patient.objects.filter(id=self.patient_id).exists():
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Patient with ID {self.patient_id} does not exist.",
                            self.patient_id,
                        )
                    )

            if method == "update":
                if not self.id:
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            "Field 'id' is required to update a patient facility address.",
                            self.id,
                        )
                    )
                elif not PatientFacilityAddressModel.objects.filter(id=self.id).exists():
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Patient facility address with ID {self.id} does not exist.",
                            self.id,
                        )
                    )

            # Must have either facility_id OR facility creation fields
            has_facility_id = self.facility_id is not None
            has_creation_fields = self._has_facility_creation_fields()

            if method == "create" and not has_facility_id and not has_creation_fields:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Either 'facility_id' or facility creation fields (facility_name, facility_city, facility_state_code, facility_postal_code) are required.",
                        None,
                    )
                )
            elif has_facility_id and has_creation_fields:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Cannot specify both 'facility_id' and facility creation fields. Use one or the other.",
                        None,
                    )
                )
            elif self.facility_id is not None:
                # Validate existing facility exists
                facility_id = self.facility_id
                if not Facility.objects.filter(id=facility_id).exists():
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Facility with ID {facility_id} does not exist.",
                            facility_id,
                        )
                    )
            elif has_creation_fields:
                # Validate required fields for facility creation
                if not self.facility_name:
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            "Field 'facility_name' is required when creating a new facility.",
                            self.facility_name,
                        )
                    )
                if not self.facility_city:
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            "Field 'facility_city' is required when creating a new facility.",
                            self.facility_city,
                        )
                    )
                if not self.facility_state_code:
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            "Field 'facility_state_code' is required when creating a new facility.",
                            self.facility_state_code,
                        )
                    )
                if not self.facility_postal_code:
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            "Field 'facility_postal_code' is required when creating a new facility.",
                            self.facility_postal_code,
                        )
                    )

            # if self.address_type and self.address_type not in [t.value for t in AddressType]:
            #     errors.append(
            #         self._create_error_detail(
            #             "value",
            #             f"Invalid address_type '{self.address_type}'. Must be one of: {[t.value for t in AddressType]}",
            #             self.address_type,
            #         )
            #     )

        if method == "delete":
            if not self.id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'id' is required to delete a patient facility address.",
                        self.id,
                    )
                )
            elif not PatientFacilityAddressModel.objects.filter(id=self.id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Patient facility address with ID {self.id} does not exist.",
                        self.id,
                    )
                )

        return errors

    def create(self) -> Effect:
        """Create a new Patient Facility Address."""
        self._validate_before_effect("create")

        payload = {"data": self.values}

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )

    def update(self) -> Effect:
        """Update an existing Patient Facility Address."""
        self._validate_before_effect("update")

        payload = {"data": self.values}

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )

    def delete(self) -> Effect:
        """Delete an existing Patient Facility Address."""
        self._validate_before_effect("delete")

        payload = {"data": {"id": str(self.id)}}

        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )


__exports__ = ("PatientFacilityAddress", "AddressType")
