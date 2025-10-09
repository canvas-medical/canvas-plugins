from canvas_sdk.v1.data import Staff
from canvas_sdk.v1.data.staff import StaffLicense
from logger import log
from pdmp_bamboo.lib.models.dtos import PractitionerDTO
from pdmp_bamboo.lib.utils.common import safe_get_attr


class PractitionerMapper:
    """Maps Canvas Staff model to PractitionerDTO."""

    # Mapping of Canvas Internal Role Codes to Bamboo Health User Role strings
    ROLE_MAPPING = {
        "PMPDEN": "Dentist",
        "PMPMI": "Medical Intern with prescriptive authority",
        "PMPMR": "Medical Resident with prescriptive authority",
        "PMPNATPHY": "Naturopathic Physician with prescriptive authority",
        "PMPNP": "Nurse Practitioner",
        "PMPOPT": "Optometrist with prescriptive authority",
        "PMPPHARM": "Pharmacist",
        "PMPPHARMRX": "Pharmacist with prescriptive authority",
        "PMPPHY": "Physician",
        "PMPPA": "Physician Assistant with prescriptive authority",
        "PMPPSY": "Psychologist with prescriptive authority",
    }

    @staticmethod
    def map_canvas_role_to_bamboo(canvas_role_code: str) -> str:
        """
        Map Canvas Internal Role Code to Bamboo Health User Role string.

        Args:
            canvas_role_code: Canvas internal role code (e.g., 'PMPPHY', 'PMPNP')

        Returns:
            Bamboo Health User Role string (e.g., 'Physician', 'Nurse Practitioner')
            Defaults to 'Physician' if no mapping found
        """
        if not canvas_role_code:
            return "Physician"

        bamboo_role = PractitionerMapper.ROLE_MAPPING.get(canvas_role_code.upper())
        if bamboo_role:
            log.info(f"Mapped role {canvas_role_code} → {bamboo_role}")
            return bamboo_role
        else:
            log.warning(f"Unknown role code '{canvas_role_code}', defaulting to Physician")
            return "Physician"

    @staticmethod
    def extract_practice_location_info(staff: Staff) -> tuple[str, str]:
        """Extract practice location ID and name from staff member."""
        try:
            if hasattr(staff, "primary_practice_location") and staff.primary_practice_location:
                practice_location = staff.primary_practice_location
                practice_location_id = str(practice_location.id)
                full_name = getattr(practice_location, "full_name", None)
                short_name = getattr(practice_location, "short_name", None)
                practice_location_name = full_name or short_name or ""
                log.info(f"Extracted practice location: {practice_location_name} (ID: {practice_location_id})")
                return practice_location_id, practice_location_name
            else:
                log.warning(f"Staff {staff.id} has no primary practice location")
        except Exception as e:
            log.error(f"Error extracting practice location: {e}")
        return "", ""

    @staticmethod
    def extract_dea_number(staff: Staff, patient_state: str | None = None) -> str:
        """
        Extract DEA number from staff member with priority-based selection.

        Priority:
        1. DEA matching patient address state and marked as primary
        2. DEA matching patient address state
        3. Primary DEA (any state)
        4. Any DEA

        Args:
            staff: Staff object
            patient_state: Patient's address state code (e.g., 'CA', 'NY')

        Returns:
            DEA number string, or empty string if none found
        """
        try:
            if not hasattr(staff, "licenses"):
                return ""

            dea_licenses = list(
                staff.licenses.filter(license_type=StaffLicense.LicenseType.DEA)
            )
            if not dea_licenses:
                return ""

            # Priority 1: State match + Primary
            if patient_state:
                for license in dea_licenses:
                    license_state = getattr(license, "state", None)
                    is_primary = getattr(license, "is_primary", False)
                    if license_state and license_state.upper() == patient_state.upper() and is_primary:
                        dea_number = getattr(license, "license_or_certification_identifier", "")
                        log.info(f"✓ DEA Priority 1 (state+primary): {dea_number} ({license_state})")
                        return dea_number

            # Priority 2: State match only
            if patient_state:
                for license in dea_licenses:
                    license_state = getattr(license, "state", None)
                    if license_state and license_state.upper() == patient_state.upper():
                        dea_number = getattr(license, "license_or_certification_identifier", "")
                        log.info(f"✓ DEA Priority 2 (state match): {dea_number} ({license_state})")
                        return dea_number

            # Priority 3: Primary DEA (any state)
            for license in dea_licenses:
                is_primary = getattr(license, "is_primary", False)
                if is_primary:
                    dea_number = getattr(license, "license_or_certification_identifier", "")
                    license_state = getattr(license, "state", None)
                    log.info(f"✓ DEA Priority 3 (primary): {dea_number} ({license_state})")
                    return dea_number

            # Priority 4: Any DEA
            if dea_licenses:
                first_license = dea_licenses[0]
                dea_number = getattr(first_license, "license_or_certification_identifier", "")
                license_state = getattr(first_license, "state", None)
                log.info(f"✓ DEA Priority 4 (first available): {dea_number} ({license_state})")
                return dea_number

            return ""

        except Exception as e:
            log.error(f"Error extracting DEA: {e}")
            return ""

    @staticmethod
    def extract_license_info(
        staff: Staff, patient_state: str | None = None
    ) -> tuple[str, str, str]:
        """
        Extract license information from staff member with priority-based selection.

        Priority:
        1. License matching patient address state and marked as primary
        2. License matching patient address state
        3. Primary license (any state)
        4. Any license

        Args:
            staff: Staff object
            patient_state: Patient's address state code (e.g., 'CA', 'NY')

        Returns:
            Tuple of (license_number, license_type, license_state)
        """
        try:
            if not hasattr(staff, "licenses"):
                return "", "", ""

            professional_licenses = list(
                staff.licenses.exclude(license_type=StaffLicense.LicenseType.DEA)
            )
            if not professional_licenses:
                return "", "", ""

            # Priority 1: State match + Primary
            if patient_state:
                for license in professional_licenses:
                    license_state = getattr(license, "state", None)
                    is_primary = getattr(license, "is_primary", False)
                    if license_state and license_state.upper() == patient_state.upper() and is_primary:
                        license_number = getattr(license, "license_or_certification_identifier", "")
                        license_type_value = getattr(license, "license_type", "Medical")
                        log.info(f"✓ License Priority 1: {license_number} ({license_type_value}, {license_state})")
                        return license_number, str(license_type_value), license_state.upper()

            # Priority 2: State match only
            if patient_state:
                for license in professional_licenses:
                    license_state = getattr(license, "state", None)
                    if license_state and license_state.upper() == patient_state.upper():
                        license_number = getattr(license, "license_or_certification_identifier", "")
                        license_type_value = getattr(license, "license_type", "Medical")
                        log.info(f"✓ License Priority 2: {license_number} ({license_type_value}, {license_state})")
                        return license_number, str(license_type_value), license_state.upper()

            # Priority 3: Primary license (any state)
            for license in professional_licenses:
                is_primary = getattr(license, "is_primary", False)
                if is_primary:
                    license_number = getattr(license, "license_or_certification_identifier", "")
                    license_state = getattr(license, "state", "")
                    license_type_value = getattr(license, "license_type", "Medical")
                    log.info(f"✓ License Priority 3: {license_number} ({license_type_value}, {license_state})")
                    return (
                        license_number,
                        str(license_type_value),
                        license_state.upper() if license_state else "",
                    )

            # Priority 4: Any license
            if professional_licenses:
                license = professional_licenses[0]
                license_number = getattr(license, "license_or_certification_identifier", "")
                license_type_value = getattr(license, "license_type", "Medical")
                license_state = getattr(license, "state", "")
                log.info(f"✓ License Priority 4: {license_number} ({license_type_value}, {license_state})")
                return (
                    license_number,
                    str(license_type_value),
                    license_state.upper() if license_state else "",
                )

            return "", "", ""

        except Exception as e:
            log.error(f"Error extracting license: {e}")
            return "", "", ""

    @staticmethod
    def extract_organization_info(staff: Staff) -> tuple[str, str]:
        """Extract organization ID and name from staff member."""
        try:
            if hasattr(staff, "primary_practice_location") and staff.primary_practice_location:
                practice_location = staff.primary_practice_location
                if hasattr(practice_location, "organization") and practice_location.organization:
                    organization = practice_location.organization
                    organization_id = str(organization.dbid)
                    full_name = getattr(organization, "full_name", None)
                    short_name = getattr(organization, "short_name", None)
                    organization_name = full_name or short_name or ""
                    log.info(f"Extracted organization: {organization_name} (ID: {organization_id})")
                    return organization_id, organization_name
        except Exception as e:
            log.error(f"Error extracting organization: {e}")
        return "", ""

    @classmethod
    def map_to_dto(cls, staff: Staff, patient_state: str | None = None) -> PractitionerDTO:
        """
        Map Staff model to PractitionerDTO.

        Args:
            staff: Canvas Staff object
            patient_state: Patient's address state code for DEA/license matching

        Returns:
            PractitionerDTO with mapped data
        """
        log.info(f"Mapping practitioner {staff.id} for state {patient_state}")

        # Extract basic staff attributes
        staff_id = safe_get_attr(staff, "id", "")
        first_name = safe_get_attr(staff, "first_name", "") or ""
        last_name = safe_get_attr(staff, "last_name", "") or ""
        middle_name = safe_get_attr(staff, "middle_name", "") or ""
        npi_number = safe_get_attr(staff, "npi_number", "") or ""
        phone = safe_get_attr(staff, "phone_number", "") or ""
        email = safe_get_attr(staff, "email", "") or ""
        active = safe_get_attr(staff, "active", True)

        # Extract DEA and license with patient state matching
        dea_number = cls.extract_dea_number(staff, patient_state)
        license_number, license_type, license_state = cls.extract_license_info(staff, patient_state)

        # Extract organization and practice location info
        organization_id, organization_name = cls.extract_organization_info(staff)
        practice_location_id, practice_location_name = cls.extract_practice_location_info(staff)

        # Map role
        canvas_role_code = safe_get_attr(staff, "role", "")
        bamboo_role = cls.map_canvas_role_to_bamboo(canvas_role_code)

        # Create DTO
        dto = PractitionerDTO(
            id=staff_id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            npi_number=npi_number,
            dea_number=dea_number,
            role=bamboo_role,
            phone=phone,
            email=email,
            active=active,
            license_number=license_number,
            license_type=license_type,
            license_state=license_state,
            organization_id=organization_id,
            organization_name=organization_name,
            practice_location_id=practice_location_id,
            practice_location_name=practice_location_name,
            errors=[],
        )

        log.info(f"Mapped practitioner: NPI={dto.npi_number}, DEA={dto.dea_number}, License={dto.license_state}")
        return dto
