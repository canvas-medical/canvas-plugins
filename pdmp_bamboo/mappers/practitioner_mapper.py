from typing import Tuple
from canvas_sdk.v1.data import Staff
from logger import log
from pdmp_bamboo.models.dtos import PractitionerDTO


def _safe_get_attr(obj, attr_name, default=None):
    """Safely get attribute from object, return default if not found."""
    try:
        return getattr(obj, attr_name, default)
    except (AttributeError, TypeError):
        return default


class PractitionerMapper:
    """Maps Canvas Staff model to PractitionerDTO."""

    @staticmethod
    def extract_practice_location_info(staff: Staff) -> tuple[str, str]:
        """Extract practice location ID and name from staff member."""
        log.info(f"PractitionerMapper: Extracting practice location info for staff: {staff.id}")

        try:
            if hasattr(staff, 'primary_practice_location') and staff.primary_practice_location:
                practice_location = staff.primary_practice_location
                practice_location_id = str(practice_location.id)
                practice_location_name = practice_location.full_name or practice_location.short_name or ""
                log.info(
                    f"PractitionerMapper: Found practice location: {practice_location_id} - {practice_location_name}")
                return practice_location_id, practice_location_name
            else:
                log.warning("PractitionerMapper: Staff has no primary practice location")

        except Exception as e:
            log.error(f"PractitionerMapper: Error extracting practice location info: {e}")

        return "", ""

    @staticmethod
    def extract_dea_number(staff: Staff) -> str:
        """Extract DEA number from staff member."""
        dea_number = ""
        try:
            nadean_number = staff.nadean_number
            if nadean_number:
                dea_number = nadean_number
        except AttributeError:
            pass

        if not dea_number:
            try:
                dea_number_attr = staff.dea_number
                if dea_number_attr:
                    dea_number = dea_number_attr
            except AttributeError:
                pass

        return dea_number

    @staticmethod
    def extract_license_info(staff: Staff) -> Tuple[str, str, str]:
        """Extract license information from staff member."""
        license_number = ""
        license_type = ""
        license_state = ""

        try:
            # Try to get professional license information
            license_number = (
                    _safe_get_attr(staff, "license_number", "")
                    or _safe_get_attr(staff, "professional_license", "")
                    or ""
            )
            license_type = _safe_get_attr(staff, "license_type", "") or "Medical"
            license_state = (
                    _safe_get_attr(staff, "license_state", "")
                    or _safe_get_attr(staff, "state", "")
                    or ""
            )
        except AttributeError:
            pass

        return license_number, license_type, license_state

    @staticmethod
    def extract_organization_info(staff: Staff) -> tuple[str, str]:
        """Extract organization ID and name from staff member."""
        log.info(f"PractitionerMapper: Extracting organization info for staff: {staff.id}")

        try:
            # Check if staff has primary_practice_location
            if hasattr(staff, 'primary_practice_location') and staff.primary_practice_location:
                practice_location = staff.primary_practice_location
                log.info(f"PractitionerMapper: Found primary practice location: {practice_location}")

                if hasattr(practice_location, 'organization') and practice_location.organization:
                    organization = practice_location.organization
                    organization_id = str(organization.dbid)
                    organization_name = organization.full_name or organization.short_name or ""
                    log.info(f"PractitionerMapper: Found organization: {organization_id} - {organization_name}")
                    return organization_id, organization_name
                else:
                    log.warning("PractitionerMapper: Practice location has no organization")
            else:
                log.warning("PractitionerMapper: Staff has no primary practice location")

        except Exception as e:
            log.error(f"PractitionerMapper: Error extracting organization info: {e}")

        return "", ""

    @classmethod
    def map_to_dto(cls, staff: Staff) -> PractitionerDTO:
        """Map Staff model to PractitionerDTO."""
        dea_number = cls.extract_dea_number(staff)
        license_number, license_type, license_state = cls.extract_license_info(staff)

        # Extract organization info
        organization_id, organization_name = cls.extract_organization_info(staff)

        # Extract practice location info
        practice_location_id, practice_location_name = cls.extract_practice_location_info(staff)

        return PractitionerDTO(
            id=_safe_get_attr(staff, "id", ""),
            first_name=_safe_get_attr(staff, "first_name", "") or "",
            last_name=_safe_get_attr(staff, "last_name", "") or "",
            middle_name=_safe_get_attr(staff, "middle_name", "") or "",
            npi_number=_safe_get_attr(staff, "npi_number", "") or "",
            dea_number=dea_number,
            role=_safe_get_attr(staff, "role", "") or "Physician",  # Default to Physician for PDMP
            phone=_safe_get_attr(staff, "phone_number", "") or "",
            email=_safe_get_attr(staff, "email", "") or "",
            active=_safe_get_attr(staff, "active", True),
            license_number=license_number,
            license_type=license_type,
            license_state=license_state,
            organization_id=organization_id,
            organization_name=organization_name,
            practice_location_id=practice_location_id,
            practice_location_name=practice_location_name,
            errors=[]
        )