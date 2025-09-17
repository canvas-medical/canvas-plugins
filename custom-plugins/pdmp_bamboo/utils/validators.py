from typing import List

from logger import log
from pdmp_bamboo.models.dtos import PatientDTO, SexCode, PractitionerDTO, OrganizationDTO, PracticeLocationDTO


class PatientValidator:
    """Validates PatientDTO data."""

    def validate(self, patient: PatientDTO) -> List[str]:
        """Validate patient data and return list of errors."""
        errors = []

        # Required fields
        if not patient.first_name:
            errors.append("❌ Patient first name is REQUIRED")
        if not patient.last_name:
            errors.append("❌ Patient last name is REQUIRED")
        if not patient.birth_date:
            errors.append("❌ Patient birth date is REQUIRED")
        if patient.sex == SexCode.UNKNOWN:
            errors.append("❌ Patient sex/gender is REQUIRED")

        # Optional but recommended fields
        if patient.address.is_empty():
            errors.append("⚠️ WARNING: Patient address is missing")
        if not patient.phone:
            errors.append("⚠️ WARNING: Patient phone number is missing")
        if not patient.ssn:
            errors.append("⚠️ WARNING: Patient SSN is missing")

        return errors

class PractitionerValidator:
    """Validates PractitionerDTO data."""

    def validate(self, practitioner: PractitionerDTO) -> List[str]:
        """Validate practitioner data and return list of errors."""
        errors = []

        # Check for required identifiers
        has_identifier = bool(practitioner.npi_number or practitioner.dea_number)

        if not has_identifier:
            errors.append(
                "❌ CRITICAL: Practitioner must have either NPI number OR DEA number for PDMP request - Please update practitioner profile in Canvas"
            )
        if not practitioner.first_name:
            errors.append(
                "❌ Practitioner first name is REQUIRED - Please update practitioner profile in Canvas"
            )
        if not practitioner.last_name:
            errors.append(
                "❌ Practitioner last name is REQUIRED - Please update practitioner profile in Canvas"
            )

        # Provide guidance on preferred identifiers
        if practitioner.npi_number and not practitioner.dea_number:
            errors.append(
                "ℹ️ INFO: NPI found but no DEA number - PDMP requests work best with both identifiers"
            )
        elif practitioner.dea_number and not practitioner.npi_number:
            errors.append(
                "ℹ️ INFO: DEA found but no NPI number - Consider adding NPI to practitioner profile"
            )

        return errors


class OrganizationValidator:
    """Validates OrganizationDTO data."""

    def validate(self, organization: OrganizationDTO) -> List[str]:
        """Validate organization data and return list of errors."""
        log.info("OrganizationValidator: Starting validation")
        log.info(f"OrganizationValidator: Organization name: '{organization.name}'")
        log.info(f"OrganizationValidator: Organization active: {organization.active}")

        errors = []

        if not organization.name:
            error_msg = "❌ Organization name is REQUIRED"
            log.error(f"OrganizationValidator: {error_msg}")
            errors.append(error_msg)
        else:
            log.info(f"OrganizationValidator: Organization name validation passed: '{organization.name}'")

        log.info(f"OrganizationValidator: Validation completed with {len(errors)} errors")
        if errors:
            log.error(f"OrganizationValidator: Validation errors: {errors}")

        return errors


class PracticeLocationValidator:
    """Validates PracticeLocationDTO data."""

    def validate(self, practice_location: PracticeLocationDTO) -> List[str]:
        """Validate practice location data and return list of errors."""
        log.info("PracticeLocationValidator: Starting validation")
        log.info(f"PracticeLocationValidator: Practice location name: '{practice_location.name}'")
        log.info(f"PracticeLocationValidator: Practice location NPI: '{practice_location.npi}'")
        log.info(f"PracticeLocationValidator: Practice location active: {practice_location.active}")

        errors = []

        # Required fields for PDMP
        if not practice_location.name:
            error_msg = "❌ Practice location name is REQUIRED"
            log.error(f"PracticeLocationValidator: {error_msg}")
            errors.append(error_msg)
        else:
            log.info(f"PracticeLocationValidator: Practice location name validation passed: '{practice_location.name}'")

        if not practice_location.npi:
            error_msg = "❌ Practice location NPI is REQUIRED for PDMP requests"
            log.error(f"PracticeLocationValidator: {error_msg}")
            errors.append(error_msg)
        else:
            log.info(f"PracticeLocationValidator: Practice location NPI validation passed: '{practice_location.npi}'")

        # Check if practice location is active
        if not practice_location.active:
            error_msg = "⚠️ WARNING: Practice location is not active"
            log.warning(f"PracticeLocationValidator: {error_msg}")
            errors.append(error_msg)

        # Validate address if present
        if practice_location.address and not practice_location.address.is_empty():
            log.info("PracticeLocationValidator: Validating practice location address")
            address = practice_location.address

            # Check for required address fields
            if not address.street:
                error_msg = "⚠️ WARNING: Practice location street address is missing"
                log.warning(f"PracticeLocationValidator: {error_msg}")
                errors.append(error_msg)

            if not address.city:
                error_msg = "⚠️ WARNING: Practice location city is missing"
                log.warning(f"PracticeLocationValidator: {error_msg}")
                errors.append(error_msg)

            if not address.state:
                error_msg = "⚠️ WARNING: Practice location state is missing"
                log.warning(f"PracticeLocationValidator: {error_msg}")
                errors.append(error_msg)

            if not address.zip_code:
                error_msg = "⚠️ WARNING: Practice location ZIP code is missing"
                log.warning(f"PracticeLocationValidator: {error_msg}")
                errors.append(error_msg)
        else:
            error_msg = "⚠️ WARNING: Practice location address is missing"
            log.warning(f"PracticeLocationValidator: {error_msg}")
            errors.append(error_msg)

        # Optional but recommended fields
        if not practice_location.phone:
            error_msg = "ℹ️ INFO: Practice location phone number is missing"
            log.info(f"PracticeLocationValidator: {error_msg}")
            errors.append(error_msg)

        # Check for DEA number (optional but useful for PDMP)
        if not practice_location.dea:
            error_msg = "ℹ️ INFO: Practice location DEA number is missing - may be required for some PDMP requests"
            log.info(f"PracticeLocationValidator: {error_msg}")
            errors.append(error_msg)

        log.info(f"PracticeLocationValidator: Validation completed with {len(errors)} errors")
        if errors:
            log.error(f"PracticeLocationValidator: Validation errors: {errors}")

        return errors