import re

from logger import log
from pdmp_bamboo.lib.models.dtos import (
    AddressDTO,
    OrganizationDTO,
    PatientDTO,
    PracticeLocationDTO,
    PractitionerDTO,
    SexCode,
)
from pdmp_bamboo.lib.utils.base_validator import BaseValidator


class PatientValidator(BaseValidator):
    """Validates PatientDTO data."""

    def validate(self, patient: PatientDTO) -> list[str]:
        """Validate patient data and return list of errors."""
        errors = []

        # Required fields
        self._validate_required(patient.first_name, "Patient first name", errors)
        self._validate_required(patient.last_name, "Patient last name", errors)
        self._validate_required(patient.birth_date, "Patient birth date", errors)
        
        if patient.sex == SexCode.UNKNOWN:
            self._add_error(errors, "Patient sex/gender is REQUIRED", "ERROR")

        # Optional but recommended fields
        if patient.address.is_empty():
            self._add_error(errors, "Patient address is missing", "WARNING")
        
        self._validate_optional(patient.phone, "Patient phone number", errors)
        self._validate_optional(patient.ssn, "Patient SSN", errors)

        return errors


class PractitionerValidator(BaseValidator):
    """Validates PractitionerDTO data."""

    def validate(self, practitioner: PractitionerDTO) -> list[str]:
        """Validate practitioner data and return list of errors."""
        errors = []

        # Check for required identifiers
        has_identifier = bool(practitioner.npi_number or practitioner.dea_number)

        if not has_identifier:
            self._add_error(
                errors,
                "CRITICAL: Practitioner must have either NPI number OR DEA number for PDMP request - Please update practitioner profile in Canvas",
                "ERROR",
            )

        self._validate_required(
            practitioner.first_name,
            "Practitioner first name - Please update practitioner profile in Canvas",
            errors,
        )
        self._validate_required(
            practitioner.last_name,
            "Practitioner last name - Please update practitioner profile in Canvas",
            errors,
        )

        # Provide guidance on preferred identifiers
        if practitioner.npi_number and not practitioner.dea_number:
            self._add_error(
                errors,
                "NPI found but no DEA number - PDMP requests work best with both identifiers",
                "INFO",
            )
        elif practitioner.dea_number and not practitioner.npi_number:
            self._add_error(
                errors,
                "DEA found but no NPI number - Consider adding NPI to practitioner profile",
                "INFO",
            )

        return errors


class OrganizationValidator(BaseValidator):
    """Validates OrganizationDTO data."""

    def validate(self, organization: OrganizationDTO) -> list[str]:
        """Validate organization data and return list of errors."""
        log.info("OrganizationValidator: Starting validation")
        log.info(f"OrganizationValidator: Organization name: '{organization.name}'")
        log.info(f"OrganizationValidator: Organization active: {organization.active}")

        errors = []

        self._validate_required(organization.name, "Organization name", errors)

        if not errors:
            log.info(
                f"OrganizationValidator: Organization name validation passed: '{organization.name}'"
            )

        log.info(f"OrganizationValidator: Validation completed with {len(errors)} errors")
        if errors:
            log.error(f"OrganizationValidator: Validation errors: {errors}")

        return errors


class PracticeLocationValidator(BaseValidator):
    """Validates PracticeLocationDTO data."""

    def validate(self, practice_location: PracticeLocationDTO) -> list[str]:
        """Validate practice location data and return list of errors."""
        log.info("PracticeLocationValidator: Starting validation")
        log.info(f"PracticeLocationValidator: Practice location name: '{practice_location.name}'")
        log.info(f"PracticeLocationValidator: Practice location NPI: '{practice_location.npi}'")
        log.info(f"PracticeLocationValidator: Practice location active: {practice_location.active}")

        errors = []

        # Required fields for PDMP
        self._validate_required(practice_location.name, "Practice location name", errors)
        self._validate_required(practice_location.npi, "Practice location NPI for PDMP requests", errors)

        if not errors:
            log.info(
                f"PracticeLocationValidator: Practice location validation passed: '{practice_location.name}'"
            )

        # Check if practice location is active
        if not practice_location.active:
            self._add_error(errors, "Practice location is not active", "WARNING")

        # Validate address if present
        if practice_location.address and not practice_location.address.is_empty():
            log.info("PracticeLocationValidator: Validating practice location address")
            address = practice_location.address

            # Check for required address fields
            self._validate_optional(address.street, "Practice location street address", errors)
            self._validate_optional(address.city, "Practice location city", errors)
            self._validate_optional(address.state, "Practice location state", errors)
            self._validate_optional(address.zip_code, "Practice location ZIP code", errors)
        else:
            self._add_error(errors, "Practice location address is missing", "WARNING")

        # Optional but recommended fields
        self._validate_info(
            not practice_location.phone,
            "Practice location phone number is missing",
            errors
        )

        # Check for DEA number (optional but useful for PDMP)
        self._validate_info(
            not practice_location.dea,
            "Practice location DEA number is missing - may be required for some PDMP requests",
            errors
        )

        log.info(f"PracticeLocationValidator: Validation completed with {len(errors)} errors")
        if errors:
            log.error(f"PracticeLocationValidator: Validation errors: {errors}")

        return errors


class AddressValidator(BaseValidator):
    """Validates AddressDTO data."""

    # Valid US state codes
    VALID_STATES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "DC"  # District of Columbia
    ]

    def validate(self, address: AddressDTO) -> list[str]:
        """
        Validate address data and return list of errors.

        Args:
            address: AddressDTO to validate

        Returns:
            List of validation errors/warnings
        """
        errors = []

        # Skip validation if address is empty (empty addresses are allowed)
        if address.is_empty():
            return errors

        log.info("AddressValidator: Validating address data")

        # Validate ZIP code format (5 digits)
        if address.zip_code and not re.match(r"^\d{5}$", address.zip_code):
            self._add_error(
                errors,
                f"Invalid ZIP code format: '{address.zip_code}' (must be 5 digits)",
                "ERROR",
            )

        # Validate ZIP+4 format (4 digits)
        if address.zip_plus_four and not re.match(r"^\d{4}$", address.zip_plus_four):
            self._add_error(
                errors,
                f"Invalid ZIP+4 format: '{address.zip_plus_four}' (must be 4 digits)",
                "ERROR",
            )

        # Validate state code
        if address.state and address.state.upper() not in self.VALID_STATES:
            self._add_error(
                errors,
                f"Invalid state code: '{address.state}' (must be 2-letter US state code)",
                "ERROR",
            )

        log.info(f"AddressValidator: Validation completed with {len(errors)} errors")

        return errors
