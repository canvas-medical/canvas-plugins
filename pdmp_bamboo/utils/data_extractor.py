"""
Data Extraction Utility for Canvas Models

This module provides comprehensive data extraction from Canvas SDK models
for patient, practitioner, and organization information for PDMP requests.
"""

from typing import Dict, Any, Optional, List, Tuple
from canvas_sdk.v1.data.patient import Patient, PatientAddress
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.organization import Organization
from canvas_sdk.v1.data.practicelocation import PracticeLocation, PracticeLocationAddress, PracticeLocationSetting
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
        patient = Patient.objects.get(id=patient_id)
        address = None
        try:
            addresses = patient.addresses
            if addresses.all():
                address = addresses.first()
        except AttributeError:
            log.info("PDMP-DataExtractor: Patient has no addresses attribute")
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
            sex_code = "U"

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
        errors.append(error_msg)
        return None, errors
    except Exception as e:
        error_msg = f"Error retrieving patient data: {str(e)}"
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
        errors.append(error_msg)
        return None, errors

    try:
        staff = Staff.objects.get(id=practitioner_id)

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

        return practitioner_data, errors

    except Staff.DoesNotExist:
        error_msg = f"Practitioner with ID '{practitioner_id}' not found"
        errors.append(error_msg)
        return None, errors
    except Exception as e:
        error_msg = f"Error retrieving practitioner data: {str(e)}"
        errors.append(error_msg)
        return None, errors


def extract_organization_data(organization_id: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Extract organization data from Canvas.
    """
    errors = []
    
    try:
        # Get organization
        organization = Organization.objects.get(dbid=organization_id)
        
        # Get practice location
        practice_location = PracticeLocation.objects.filter(active=True).first()
        # address_count = practice_location.addresses.count()
        # log.info(f"PDMP-DataExtractor: Found {address_count} addresses")


        if practice_location:
            # Extract practice location data including address
            practice_location_data = _extract_practice_location_data(practice_location)
            
            organization_data = {
                "id": str(organization.dbid),
                "name": organization.full_name or organization.short_name,
                "practice_location": practice_location_data
            }
            
            log.info(f"PDMP-DataExtractor: Organization data extracted: {organization_data['name']}")
            return organization_data, errors
        else:
            errors.append("No active practice location found")
            return None, errors
            
    except Organization.DoesNotExist:
        errors.append(f"Organization with ID {organization_id} not found")
        return None, errors
    except Exception as e:
        errors.append(f"Error extracting organization data: {str(e)}")
        log.error(f"PDMP-DataExtractor: Error extracting organization data: {e}")
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
        # Extract organization data - get organization_id first
        organization_data = None
        organization_errors = []

        try:
            # Try to get organization from practitioner first
            organization_id = None
            if practitioner_data and practitioner_data.get("organization_id"):
                organization_id = practitioner_data["organization_id"]
                log.info(f"PDMP-DataExtractor: Found organization_id from practitioner: {organization_id}")
            else:
                # Fallback: get first active organization
                log.info("PDMP-DataExtractor: No organization_id from practitioner, trying to get active organization")
                try:
                    from canvas_sdk.v1.data import Organization
                    organization = Organization.objects.filter(active=True).first()
                    if organization:
                        organization_id = str(organization.dbid)
                        log.info(f"PDMP-DataExtractor: Found active organization with ID: {organization_id}")
                    else:
                        log.warning("PDMP-DataExtractor: No active organization found")
                        organization_errors.append("No active organization found")
                except Exception as e:
                    log.error(f"PDMP-DataExtractor: Error getting organization: {e}")
                    organization_errors.append(f"Error getting organization: {str(e)}")

            if organization_id:
                organization_data, organization_errors = extract_organization_data(organization_id)
                all_errors.extend(organization_errors)
            else:
                log.warning("PDMP-DataExtractor: No organization_id available, skipping organization data extraction")
                organization_errors.append("No organization_id available")

        except Exception as e:
            log.error(f"PDMP-DataExtractor: Error in organization data extraction: {e}")
            organization_errors.append(f"Error in organization data extraction: {str(e)}")
            all_errors.extend(organization_errors)

        # Add this logging after organization data extraction:
        log.info("=" * 80)
        log.info("PDMP-DataExtractor: RAW CANVAS API RESPONSES")
        log.info("=" * 80)

        # Log raw organization data
        log.info("RAW ORGANIZATION DATA FROM CANVAS:")
        log.info(f"  Raw organization response: {organization_data}")

        # Log raw practice location data
        practice_location = organization_data.get("practice_location", {})
        log.info("RAW PRACTICE LOCATION DATA FROM CANVAS:")
        log.info(f"  Raw practice_location: {practice_location}")

        # Log raw address data
        address = practice_location.get("address", {})
        log.info("RAW ADDRESS DATA FROM CANVAS:")
        log.info(f"  Raw address: {address}")
        log.info(f"  Address keys: {list(address.keys())}")
        log.info(f"  Address values: {list(address.values())}")

        # Log each address field individually
        log.info("INDIVIDUAL ADDRESS FIELDS:")
        for key, value in address.items():
            log.info(f"    {key}: '{value}'")

        log.info("=" * 80)

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

    log.info(f"PDMP-DataExtractor: Extracting practice location data for ID: {practice_location.id}")
    log.info(f"PDMP-DataExtractor: Practice location type: {type(practice_location)}")

    # Extract address information from practice location
    address_data = {}
    try:
        # Try direct query approach first to avoid relationship issues
        log.info("PDMP-DataExtractor: Trying direct query approach for addresses...")

        # Query addresses directly using the practice location ID
        addresses = practice_location.addresses.all()  # This should return PracticeLocationAddress objects

        if addresses.exists():
            address = addresses.first()
            log.info(f"PDMP-DataExtractor: Direct query first address: {address}")
            log.info(f"PDMP-DataExtractor: Address type: {type(address)}")

            # Log all address fields
            for attr in ['line1', 'line2', 'city', 'district', 'state_code', 'postal_code', 'use', 'type']:
                value = getattr(address, attr, 'NOT_FOUND')
                log.info(f"PDMP-DataExtractor: Address.{attr}: {value}")

            address_data = {
                "street": _safe_get_attr(address, "line1", "") or "",
                "street2": _safe_get_attr(address, "line2", "") or "",
                "city": _safe_get_attr(address, "city", "") or "",
                "state": _safe_get_attr(address, "state_code", "") or "",
                "zip_code": _safe_get_attr(address, "postal_code", "") or "",
                "zip_plus_four": "",  # Not available in this model
            }
            log.info(f"PDMP-DataExtractor: Direct query extracted address data: {address_data}")
        else:
            log.info("PDMP-DataExtractor: Direct query found no addresses")

            # Try relationship approach as fallback
            log.info("PDMP-DataExtractor: Trying relationship approach as fallback...")
            if practice_location and hasattr(practice_location, 'addresses'):
                try:
                    addresses_queryset = practice_location.addresses
                    address_count = addresses_queryset.count()
                    log.info(f"PDMP-DataExtractor: Relationship found {address_count} addresses")

                    if address_count > 0:
                        address = addresses_queryset.first()
                        log.info(f"PDMP-DataExtractor: Relationship first address: {address}")

                        address_data = {
                            "street": _safe_get_attr(address, "line1", "") or "",
                            "street2": _safe_get_attr(address, "line2", "") or "",
                            "city": _safe_get_attr(address, "city", "") or "",
                            "state": _safe_get_attr(address, "state_code", "") or "",
                            "zip_code": _safe_get_attr(address, "postal_code", "") or "",
                            "zip_plus_four": "",  # Not available in this model
                        }
                        log.info(f"PDMP-DataExtractor: Relationship extracted address data: {address_data}")
                except Exception as rel_error:
                    log.error(f"PDMP-DataExtractor: Error in relationship approach: {rel_error}")
                    import traceback
                    log.error(f"PDMP-DataExtractor: Relationship error traceback: {traceback.format_exc()}")
            else:
                log.warning("PDMP-DataExtractor: No addresses relationship available")

    except Exception as e:
        log.error(f"PDMP-DataExtractor: Error in address extraction: {e}")
        import traceback
        log.error(f"PDMP-DataExtractor: Address extraction traceback: {traceback.format_exc()}")

    # If no address found, use empty data
    if not address_data:
        address_data = {
            "street": "",
            "street2": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "zip_plus_four": "",
        }
        log.warning("PDMP-DataExtractor: Using empty address data")

    return {
        "id": _safe_get_attr(practice_location, "id", ""),
        "name": _safe_get_attr(practice_location, "full_name", "") or _safe_get_attr(practice_location, "name",
                                                                                     "") or "",
        "npi": _safe_get_attr(practice_location, "npi_number", "") or "",
        "dea": _safe_get_attr(practice_location, "dea_number", "AB1234579") or "", #TODO: HARDCODED for now
        "ncpdp": _safe_get_attr(practice_location, "ncpdp_number", "") or "",
        "phone": _safe_get_attr(practice_location, "phone_number", "") or "",
        "active": _safe_get_attr(practice_location, "active", True),
        "address": address_data,
    }