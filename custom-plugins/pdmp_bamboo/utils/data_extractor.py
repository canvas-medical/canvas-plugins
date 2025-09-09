"""
Data Extraction Utility for Canvas Models

This module provides comprehensive data extraction from Canvas SDK models
for patient, practitioner, and organization information for PDMP requests.
"""

from typing import Dict, Any, Optional, List, Tuple
from canvas_sdk.v1.data.patient import Patient, PatientAddress
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.organization import Organization
from canvas_sdk.v1.data.practicelocation import PracticeLocation
from logger import log


def extract_patient_data(patient_id: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Extract patient data from Canvas SDK models for PDMP request.

    Args:
        patient_id: The patient identifier

    Returns:
        Tuple containing:
        - patient_data: Dict with patient information (None if extraction fails)
        - errors: List of validation error messages (empty if no errors)
    """
    errors = []

    try:
        log.info(
            f"PDMP-DataExtractor: Starting patient data extraction for patient_id={patient_id}"
        )

        patient = Patient.objects.get(id=patient_id)
        log.info(f"PDMP-DataExtractor: Successfully retrieved patient: {patient}")

        # Get patient address (sandbox-safe)
        address = None
        try:
            addresses = patient.addresses
            if addresses.all():
                address = addresses.first()
                log.info(f"PDMP-DataExtractor: Found patient address: {address}")
        except AttributeError:
            log.info("PDMP-DataExtractor: Patient has no addresses attribute")

        # Normalize sex code for PDMP (sandbox-safe)
        try:
            sex_code = patient.sex_at_birth or ""
        except AttributeError:
            sex_code = ""

        if sex_code.upper() in ["UNK", "UNKNOWN", "U"]:
            sex_code = "U"
        elif sex_code.upper() in ["MALE", "M"]:
            sex_code = "M"
        elif sex_code.upper() in ["FEMALE", "F"]:
            sex_code = "F"
        else:
            sex_code = "U"  # Default to unknown for PDMP

        # Build patient data for PDMP XML (sandbox-safe attribute access)
        patient_data = {
            "id": _safe_get_attr(patient, "id", ""),
            "first_name": _safe_get_attr(patient, "first_name", "") or "",
            "last_name": _safe_get_attr(patient, "last_name", "") or "",
            "middle_name": _safe_get_attr(patient, "middle_name", "") or "",
            "birth_date": _get_formatted_birth_date(patient),
            "sex": sex_code,
            "phone": _safe_get_attr(patient, "phone_number", "") or "",
            "address": _extract_address_data(address),
            "ssn": _safe_get_attr(patient, "ssn", "") or "",
            "mrn": _safe_get_attr(patient, "mrn", "") or "",
        }

        # Check for required fields (based on PDMP working sample requirements)
        if not patient_data["first_name"]:
            errors.append(
                "❌ Patient first name is REQUIRED - Please update patient demographics in Canvas"
            )
        if not patient_data["last_name"]:
            errors.append(
                "❌ Patient last name is REQUIRED - Please update patient demographics in Canvas"
            )
        if not patient_data["birth_date"]:
            errors.append(
                "❌ Patient birth date is REQUIRED - Please set birth date in Canvas patient record"
            )
        if not patient_data["sex"]:
            errors.append(
                "❌ Patient sex/gender is REQUIRED - Please set patient sex in Canvas demographics"
            )

        # Check for important but not critical fields
        address_data = patient_data.get("address", {})
        if not any(address_data.values()):
            errors.append(
                "⚠️ WARNING: Patient address is missing - PDMP requests work better with complete address information"
            )
        if not patient_data.get("phone"):
            errors.append(
                "⚠️ WARNING: Patient phone number is missing - Consider adding for better PDMP results"
            )
        if not patient_data.get("ssn"):
            errors.append(
                "⚠️ WARNING: Patient SSN is missing - PDMP matching is more accurate with SSN"
            )

        log.info(
            f"PDMP-DataExtractor: Patient data extracted: {patient_data['first_name']} {patient_data['last_name']}"
        )
        return patient_data, errors

    except Patient.DoesNotExist:
        error_msg = f"Patient with ID '{patient_id}' not found"
        log.error(f"PDMP-DataExtractor: {error_msg}")
        errors.append(error_msg)
        return None, errors
    except Exception as e:
        error_msg = f"Error retrieving patient data: {str(e)}"
        log.error(f"PDMP-DataExtractor: {error_msg}")
        errors.append(error_msg)
        return None, errors


def extract_practitioner_data(
    practitioner_id: Optional[str],
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Extract practitioner data from Canvas SDK models for PDMP request.

    Args:
        practitioner_id: The practitioner identifier

    Returns:
        Tuple containing:
        - practitioner_data: Dict with practitioner information (None if extraction fails)
        - errors: List of validation error messages (empty if no errors)
    """
    errors = []

    if not practitioner_id:
        error_msg = "Practitioner ID is required for PDMP request"
        log.error(f"PDMP-DataExtractor: {error_msg}")
        errors.append(error_msg)
        return None, errors

    try:
        log.info(
            f"PDMP-DataExtractor: Starting practitioner data extraction for practitioner_id={practitioner_id}"
        )

        staff = Staff.objects.get(id=practitioner_id)
        log.info(f"PDMP-DataExtractor: Successfully retrieved staff: {staff}")

        # Get DEA number - try multiple possible field names (sandbox-safe)
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

        # Try to extract license information (sandbox-safe)
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

        # Build practitioner data for PDMP XML (sandbox-safe)
        practitioner_data = {
            "id": _safe_get_attr(staff, "id", ""),
            "first_name": _safe_get_attr(staff, "first_name", "") or "",
            "last_name": _safe_get_attr(staff, "last_name", "") or "",
            "middle_name": _safe_get_attr(staff, "middle_name", "") or "",
            "npi_number": _safe_get_attr(staff, "npi_number", "") or "",
            "dea_number": dea_number,
            "role": _safe_get_attr(staff, "role", "")
            or "Physician",  # Default to Physician for PDMP
            "phone": _safe_get_attr(staff, "phone_number", "") or "",
            "email": _safe_get_attr(staff, "email", "") or "",
            "active": _safe_get_attr(staff, "active", True),
            "license_number": license_number,
            "license_type": license_type,
            "license_state": license_state,
        }

        # Check for required fields (based on PDMP working sample requirements)
        has_identifier = bool(practitioner_data["npi_number"] or practitioner_data["dea_number"])

        if not has_identifier:
            errors.append(
                "❌ CRITICAL: Practitioner must have either NPI number OR DEA number for PDMP request - Please update practitioner profile in Canvas"
            )
        if not practitioner_data["first_name"]:
            errors.append(
                "❌ Practitioner first name is REQUIRED - Please update practitioner profile in Canvas"
            )
        if not practitioner_data["last_name"]:
            errors.append(
                "❌ Practitioner last name is REQUIRED - Please update practitioner profile in Canvas"
            )

        # Provide guidance on preferred identifiers
        if practitioner_data["npi_number"] and not practitioner_data["dea_number"]:
            errors.append(
                "ℹ️ INFO: NPI found but no DEA number - PDMP requests work best with both identifiers"
            )
        elif practitioner_data["dea_number"] and not practitioner_data["npi_number"]:
            errors.append(
                "ℹ️ INFO: DEA found but no NPI number - Consider adding NPI to practitioner profile"
            )

        log.info(
            f"PDMP-DataExtractor: Practitioner data extracted: {practitioner_data['first_name']} {practitioner_data['last_name']} (NPI: {practitioner_data['npi_number']})"
        )
        return practitioner_data, errors

    except Staff.DoesNotExist:
        error_msg = f"Practitioner with ID '{practitioner_id}' not found"
        log.error(f"PDMP-DataExtractor: {error_msg}")
        errors.append(error_msg)
        return None, errors
    except Exception as e:
        error_msg = f"Error retrieving practitioner data: {str(e)}"
        log.error(f"PDMP-DataExtractor: {error_msg}")
        errors.append(error_msg)
        return None, errors


def extract_organization_data() -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Extract organization data from Canvas SDK models for PDMP request.

    Returns:
        Tuple containing:
        - organization_data: Dict with organization information (None if extraction fails)
        - errors: List of validation error messages (empty if no errors)
    """
    errors = []

    try:
        log.info("PDMP-DataExtractor: Starting organization data extraction")

        # Try to get the main organization first
        organization = Organization.objects.filter(active=True).first()
        if not organization:
            error_msg = "No active organization found in Canvas"
            log.error(f"PDMP-DataExtractor: {error_msg}")
            errors.append(error_msg)
            return None, errors

        # Get the main location from the organization (sandbox-safe)
        practice_location = None
        try:
            practice_location = organization.main_location
        except AttributeError:
            pass

        # If no main location, try to get the first active practice location
        if not practice_location:
            practice_location = PracticeLocation.objects.filter(active=True).first()

        # Build organization data for PDMP XML (sandbox-safe)
        organization_data = {
            "id": _safe_get_attr(organization, "id", ""),
            "name": _safe_get_attr(organization, "name", "") or "",
            "group_npi": _safe_get_attr(organization, "group_npi_number", "") or "",
            "active": _safe_get_attr(organization, "active", True),
            "practice_location": _extract_practice_location_data(practice_location)
            if practice_location
            else None,
        }

        # Check for required fields - location needs at least one identifier
        if organization_data["practice_location"]:
            has_location_identifier = bool(
                organization_data["practice_location"]["npi"] or organization_data["group_npi"]
            )

            if not has_location_identifier:
                errors.append(
                    "❌ CRITICAL: Organization/Practice location must have NPI number for PDMP request - Please update organization settings in Canvas"
                )

            # Provide guidance about location data quality
            if not organization_data.get("name"):
                errors.append(
                    "⚠️ WARNING: Organization name is missing - Please set organization name in Canvas"
                )

        else:
            errors.append(
                "❌ CRITICAL: Practice location information is required for PDMP request - Please configure practice locations in Canvas"
            )

        log.info(f"PDMP-DataExtractor: Organization data extracted: {organization_data['name']}")
        return organization_data, errors

    except Exception as e:
        error_msg = f"Error retrieving organization data: {str(e)}"
        log.error(f"PDMP-DataExtractor: {error_msg}")
        errors.append(error_msg)
        return None, errors


def extract_all_data_for_pdmp(
    patient_id: str, practitioner_id: Optional[str]
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Extract all required data from Canvas for PDMP request.

    Args:
        patient_id: The patient identifier
        practitioner_id: The practitioner identifier

    Returns:
        Tuple containing:
        - all_data: Dict with all extracted data (None if critical extraction fails)
        - errors: List of all validation error messages
    """
    log.info(
        f"PDMP-DataExtractor: Starting comprehensive data extraction for PDMP request - patient_id={patient_id}, practitioner_id={practitioner_id}"
    )

    all_errors = []

    try:
        # Extract patient data
        patient_data, patient_errors = extract_patient_data(patient_id)
        all_errors.extend(patient_errors)
        log.info(
            f"PDMP-DataExtractor: Patient data extraction completed. Success: {bool(patient_data)}, Errors: {len(patient_errors)}"
        )

        # Extract practitioner data
        practitioner_data, practitioner_errors = extract_practitioner_data(practitioner_id)
        all_errors.extend(practitioner_errors)
        log.info(
            f"PDMP-DataExtractor: Practitioner data extraction completed. Success: {bool(practitioner_data)}, Errors: {len(practitioner_errors)}"
        )

        # Extract organization data
        organization_data, organization_errors = extract_organization_data()
        all_errors.extend(organization_errors)
        log.info(
            f"PDMP-DataExtractor: Organization data extraction completed. Success: {bool(organization_data)}, Errors: {len(organization_errors)}"
        )

        # Combine all data
        all_data = {
            "patient": patient_data,
            "practitioner": practitioner_data,
            "organization": organization_data,
            "extraction_errors": all_errors,
        }

        log.info(f"PDMP-DataExtractor: Data extraction complete - {len(all_errors)} errors found")
        return all_data, all_errors

    except Exception as e:
        log.error(f"PDMP-DataExtractor: Error in extract_all_data_for_pdmp: {str(e)}")
        import traceback

        log.error(f"PDMP-DataExtractor: Traceback: {traceback.format_exc()}")
        return None, [f"Critical error in data extraction: {str(e)}"]


# Helper functions for sandbox-safe attribute access


def _safe_get_attr(obj: Any, attr_name: str, default: Any = None) -> Any:
    """Safely get attribute value without using getattr (Canvas sandbox restriction)."""
    try:
        return obj.__dict__.get(attr_name, default) or default
    except (AttributeError, TypeError):
        # Fallback to direct attribute access
        try:
            value = None
            if attr_name == "id":
                value = obj.id
            elif attr_name == "first_name":
                value = obj.first_name
            elif attr_name == "last_name":
                value = obj.last_name
            elif attr_name == "middle_name":
                value = obj.middle_name
            elif attr_name == "phone_number":
                value = obj.phone_number
            elif attr_name == "email":
                value = obj.email
            elif attr_name == "ssn":
                value = obj.ssn
            elif attr_name == "mrn":
                value = obj.mrn
            elif attr_name == "npi_number":
                value = obj.npi_number
            elif attr_name == "role":
                value = obj.role
            elif attr_name == "active":
                value = obj.active
            elif attr_name == "name":
                value = obj.name
            elif attr_name == "group_npi_number":
                value = obj.group_npi_number
            elif attr_name == "full_name":
                value = obj.full_name

            return value if value is not None else default
        except AttributeError:
            return default


def _get_formatted_birth_date(patient: Patient) -> str:
    """Safely get formatted birth date."""
    try:
        birth_date = patient.birth_date
        if birth_date:
            return birth_date.strftime("%Y-%m-%d")
    except AttributeError:
        pass
    return ""


def _extract_address_data(address: Optional[PatientAddress]) -> Dict[str, str]:
    """Extract address data safely."""
    if not address:
        return {
            "street": "",
            "street2": "",
            "city": "",
            "state": "",
            "zip_code": "",
        }

    return {
        "street": _safe_get_attr(address, "line1", "") or "",
        "street2": _safe_get_attr(address, "line2", "") or "",
        "city": _safe_get_attr(address, "city", "") or "",
        "state": _safe_get_attr(address, "state_code", "") or "",
        "zip_code": _safe_get_attr(address, "postal_code", "") or "",
    }


def _extract_practice_location_data(practice_location: Any) -> Dict[str, Any]:
    """Extract comprehensive practice location data safely."""

    # Extract address information from practice location
    address_data = {}
    try:
        # Try to get address from practice location
        if practice_location and practice_location.address:
            address_data = {
                "street": _safe_get_attr(practice_location.address, "line1", "") or "",
                "street2": _safe_get_attr(practice_location.address, "line2", "") or "",
                "city": _safe_get_attr(practice_location.address, "city", "") or "",
                "state": _safe_get_attr(practice_location.address, "state_code", "") or "",
                "zip_code": _safe_get_attr(practice_location.address, "postal_code", "") or "",
                "zip_plus_four": _safe_get_attr(practice_location.address, "zip_plus_four", "")
                or "",
            }
    except AttributeError:
        # Fallback: try direct attribute access
        address_data = {
            "street": _safe_get_attr(practice_location, "street", "") or "",
            "street2": _safe_get_attr(practice_location, "street2", "") or "",
            "city": _safe_get_attr(practice_location, "city", "") or "",
            "state": _safe_get_attr(practice_location, "state", "") or "",
            "zip_code": _safe_get_attr(practice_location, "zip_code", "") or "",
            "zip_plus_four": "",
        }

    return {
        "id": _safe_get_attr(practice_location, "id", ""),
        "name": _safe_get_attr(practice_location, "full_name", "")
        or _safe_get_attr(practice_location, "name", "")
        or "",
        "npi": _safe_get_attr(practice_location, "npi_number", "") or "",
        "dea": _safe_get_attr(practice_location, "dea_number", "") or "",
        "ncpdp": _safe_get_attr(practice_location, "ncpdp_number", "") or "",
        "phone": _safe_get_attr(practice_location, "phone_number", "") or "",
        "active": _safe_get_attr(practice_location, "active", True),
        "address": address_data,
    }
