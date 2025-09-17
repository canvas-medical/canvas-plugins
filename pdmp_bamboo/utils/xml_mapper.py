"""
XML Template Mapping Utility for PDMP Requests

This module provides functionality to map Canvas data to PDMP XML template
for BambooHealth PMP Gateway requests using real extracted data.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from logger import log

# Configuration values - software identification for PDMP requests
HARDCODED_VALUES = {
    "software": {"developer": "Canvas Medical", "product": "Canvas EMR", "version": "1.0.0"},
}


def _get_dynamic_date_range() -> Dict[str, str]:
    """
    Calculate dynamic date range from current date back 2 years.

    Returns:
        Dictionary with 'begin' and 'end' date strings in YYYY-MM-DD format
    """
    current_date = datetime.now()
    two_years_ago = current_date - timedelta(days=730)  # Approximately 2 years

    return {"begin": two_years_ago.strftime("%Y-%m-%d"), "end": current_date.strftime("%Y-%m-%d")}

# TODO: ovo verovatno nije kako treba!
def _get_pmp_destination(organization_data: Dict[str, Any]) -> str:
    """
    Determine PMP destination state code based on organization location.

    Args:
        organization_data: Dictionary containing organization and practice location data

    Returns:
        Two-letter state code for PMP destination, defaults to "KS" if cannot be determined
    """
    if not organization_data:
        log.warning(
            "PDMP-XMLMapper: No organization data available, defaulting PMP destination to KS"
        )
        return "KS"

    # Try to get state from practice location address
    practice_location = organization_data.get("practice_location", {})
    if practice_location:
        address = practice_location.get("address", {})
        state_code = address.get("state", "").strip().upper()

        if state_code and len(state_code) == 2:
            log.info(f"PDMP-XMLMapper: Using PMP destination from practice location: {state_code}")
            return state_code

    # If we can't determine state, log warning and default to Kansas
    log.warning("PDMP-XMLMapper: Cannot determine state from practice location, defaulting to KS")
    return "CA" # TODO: Why defaulting to KS?


def _validate_patient_request_data(canvas_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that we have all required fields for a successful PatientRequest.
    Returns errors for missing required fields.
    
    Returns:
        Dict with validation results: {"valid": bool, "errors": List[str], "data": Dict}
    """
    log.info("PDMP-XMLMapper: Validating required fields for PatientRequest")
    
    # Extract data
    patient_data = canvas_data.get("patient", {})
    practitioner_data = canvas_data.get("practitioner", {})
    organization_data = canvas_data.get("organization", {})
    
    validation_errors = []
    
    # Validate patient data
    if not patient_data.get("first_name"):
        validation_errors.append("Missing patient first_name")
    
    if not patient_data.get("last_name"):
        validation_errors.append("Missing patient last_name")
    
    if not patient_data.get("birth_date"):
        validation_errors.append("Missing patient birth_date")
    
    # Validate practitioner data
    if not practitioner_data.get("first_name"):
        validation_errors.append("Missing practitioner first_name")
    
    if not practitioner_data.get("last_name"):
        validation_errors.append("Missing practitioner last_name")
    
    if not practitioner_data.get("dea_number"):
        validation_errors.append("Missing practitioner dea_number")
    
    # Validate organization data (practice_location)
    practice_location = organization_data.get("practice_location", {})
    if not practice_location.get("name"):
        validation_errors.append("Missing practice_location name")
    
    if not practice_location.get("dea"):
        validation_errors.append("Missing practice_location dea")
    
    if not practice_location.get("npi"):
        validation_errors.append("Missing practice_location npi")
    
    # Validate location address or NCPDP
    address = practice_location.get("address", {})
    has_address = any(address.values())
    has_ncpdp = bool(practice_location.get("ncpdp"))
    
    log.info(f"PDMP-XMLMapper: Address validation - has_address: {has_address}, has_ncpdp: {has_ncpdp}")
    log.info(f"PDMP-XMLMapper: Address values: {address}")
    log.info(f"PDMP-XMLMapper: NCPDP value: '{practice_location.get('ncpdp', 'MISSING')}'")
    
    if not has_address and not has_ncpdp:
        validation_errors.append("Missing practice_location address or NCPDP number (at least one is required)")
        log.error(f"PDMP-XMLMapper: Address validation failed - address values: {address}, NCPDP: '{practice_location.get('ncpdp', 'MISSING')}'")
    
    # Log validation results
    if validation_errors:
        log.error(f"PDMP-XMLMapper: PatientRequest validation failed with {len(validation_errors)} errors:")
        for error in validation_errors:
            log.error(f"  - {error}")
        return {
            "valid": False,
            "errors": validation_errors,
            "data": None
        }
    else:
        log.info("PDMP-XMLMapper: All required fields present, PatientRequest validation successful")
        return {
            "valid": True,
            "errors": [],
            "data": {
                "patient": patient_data,
                "practitioner": practitioner_data,
                "organization": organization_data
            }
        }


def create_pdmp_xml(canvas_data: Dict[str, Any]) -> str:
    """
    Create PDMP XML PATIENT request from Canvas data with validation.
    Raises ValueError if required data is missing.
    """
    log.info("PDMP-XMLMapper: Creating PatientRequest XML")
    
    # Log ALL extracted data for debugging
    log.info("=" * 80)
    log.info("PDMP-XMLMapper: FULL EXTRACTED DATA DEBUG")
    log.info("=" * 80)
    
    patient_data = canvas_data.get("patient", {})
    practitioner_data = canvas_data.get("practitioner", {})
    organization_data = canvas_data.get("organization", {})
    
    log.info("PATIENT DATA:")
    log.info(f"  Raw patient_data: {patient_data}")
    log.info(f"  First Name: '{patient_data.get('first_name', 'MISSING')}'")
    log.info(f"  Last Name: '{patient_data.get('last_name', 'MISSING')}'")
    log.info(f"  Birth Date: '{patient_data.get('birth_date', 'MISSING')}'")
    log.info(f"  Sex: '{patient_data.get('sex', 'MISSING')}'")
    log.info(f"  MRN: '{patient_data.get('mrn', 'MISSING')}'")
    log.info(f"  SSN: '{patient_data.get('ssn', 'MISSING')}'")
    log.info(f"  Phone: '{patient_data.get('phone', 'MISSING')}'")
    
    address_data = patient_data.get("address", {})
    log.info("  PATIENT ADDRESS:")
    log.info(f"    Street: '{address_data.get('street', 'MISSING')}'")
    log.info(f"    Street2: '{address_data.get('street2', 'MISSING')}'")
    log.info(f"    City: '{address_data.get('city', 'MISSING')}'")
    log.info(f"    State: '{address_data.get('state', 'MISSING')}'")
    log.info(f"    Zip Code: '{address_data.get('zip_code', 'MISSING')}'")
    log.info(f"    Zip Plus Four: '{address_data.get('zip_plus_four', 'MISSING')}'")
    
    log.info("PRACTITIONER DATA:")
    log.info(f"  Raw practitioner_data: {practitioner_data}")
    log.info(f"  First Name: '{practitioner_data.get('first_name', 'MISSING')}'")
    log.info(f"  Last Name: '{practitioner_data.get('last_name', 'MISSING')}'")
    log.info(f"  Middle Name: '{practitioner_data.get('middle_name', 'MISSING')}'")
    log.info(f"  DEA Number: '{practitioner_data.get('dea_number', 'MISSING')}'")
    log.info(f"  NPI Number: '{practitioner_data.get('npi_number', 'MISSING')}'")
    log.info(f"  Role: '{practitioner_data.get('role', 'MISSING')}'")
    log.info(f"  License Number: '{practitioner_data.get('license_number', 'MISSING')}'")
    log.info(f"  License Type: '{practitioner_data.get('license_type', 'MISSING')}'")
    log.info(f"  License State: '{practitioner_data.get('license_state', 'MISSING')}'")
    log.info(f"  Phone: '{practitioner_data.get('phone', 'MISSING')}'")
    log.info(f"  Email: '{practitioner_data.get('email', 'MISSING')}'")
    log.info(f"  Active: '{practitioner_data.get('active', 'MISSING')}'")
    
    log.info("ORGANIZATION DATA:")
    log.info(f"  Raw organization_data: {organization_data}")
    log.info(f"  Organization Name: '{organization_data.get('name', 'MISSING')}'")
    log.info(f"  Group NPI: '{organization_data.get('group_npi', 'MISSING')}'")
    log.info(f"  Active: '{organization_data.get('active', 'MISSING')}'")
    
    practice_location = organization_data.get("practice_location", {})
    log.info("  PRACTICE LOCATION:")
    log.info(f"    Raw practice_location: {practice_location}")
    log.info(f"    ID: '{practice_location.get('id', 'MISSING')}'")
    log.info(f"    Name: '{practice_location.get('name', 'MISSING')}'")
    log.info(f"    NPI: '{practice_location.get('npi', 'MISSING')}'")
    log.info(f"    DEA: '{practice_location.get('dea', 'MISSING')}'")
    log.info(f"    NCPDP: '{practice_location.get('ncpdp', 'MISSING')}'")
    log.info(f"    Phone: '{practice_location.get('phone', 'MISSING')}'")
    log.info(f"    Active: '{practice_location.get('active', 'MISSING')}'")
    
    practice_address = practice_location.get("address", {})
    log.info("    PRACTICE LOCATION ADDRESS:")
    log.info(f"      Street: '{practice_address.get('street', 'MISSING')}'")
    log.info(f"      Street2: '{practice_address.get('street2', 'MISSING')}'")
    log.info(f"      City: '{practice_address.get('city', 'MISSING')}'")
    log.info(f"      State: '{practice_address.get('state', 'MISSING')}'")
    log.info(f"      Zip Code: '{practice_address.get('zip_code', 'MISSING')}'")
    log.info(f"      Zip Plus Four: '{practice_address.get('zip_plus_four', 'MISSING')}'")
    
    # Check address validation
    has_address = any(practice_address.values())
    has_ncpdp = bool(practice_location.get("ncpdp"))
    log.info("    ADDRESS VALIDATION:")
    log.info(f"      Has any address values: {has_address}")
    log.info(f"      Has NCPDP: {has_ncpdp}")
    log.info(f"      Address values: {list(practice_address.values())}")
    log.info(f"      Non-empty address values: {[v for v in practice_address.values() if v]}")
    
    log.info("=" * 80)
    
    # Validate data first
    validation_result = _validate_patient_request_data(canvas_data)
    
    if not validation_result["valid"]:
        error_msg = f"PDMP-XMLMapper: Cannot create PatientRequest XML due to validation errors: {', '.join(validation_result['errors'])}"
        log.error(error_msg)
        raise ValueError(error_msg)
    
    # Extract validated data
    validated_data = validation_result["data"]
    patient_data = validated_data.get("patient", {})
    practitioner_data = validated_data.get("practitioner", {})
    organization_data = validated_data.get("organization", {})

    # Generate unique request ID
    request_id = str(uuid.uuid4())

    # Get dynamic date range
    date_range = _get_dynamic_date_range()

    # Get PMP destination from organization data
    pmp_destination = _get_pmp_destination(organization_data)

    log.info(f"PDMP-XMLMapper: Generated request ID: {request_id}")
    log.info(f"PDMP-XMLMapper: Using date range: {date_range['begin']} to {date_range['end']}")
    log.info(f"PDMP-XMLMapper: Using PMP destination: {pmp_destination}")
    log.info(f"PDMP-XMLMapper: Mapping patient: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}")
    log.info(f"PDMP-XMLMapper: Mapping practitioner: {practitioner_data.get('first_name', '')} {practitioner_data.get('last_name', '')}")
    log.info(f"PDMP-XMLMapper: Mapping organization: {organization_data.get('name', '')}")

    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatientRequest xmlns="http://xml.appriss.com/gateway/v5_1">
  <Requester>
    <LicenseeRequestId>{request_id}</LicenseeRequestId>
    <SenderSoftware>
      <Developer>{HARDCODED_VALUES["software"]["developer"]}</Developer>
      <Product>{HARDCODED_VALUES["software"]["product"]}</Product>
      <Version>{HARDCODED_VALUES["software"]["version"]}</Version>
    </SenderSoftware>
    <RequestDestinations>
      <Pmp>{pmp_destination}</Pmp>
    </RequestDestinations>
    {_build_provider_section(practitioner_data)}
    {_build_location_section(organization_data)}
  </Requester>
  <PrescriptionRequest>
    <DateRange>
      <Begin>{date_range["begin"]}</Begin>
      <End>{date_range["end"]}</End>
    </DateRange>
    <Coverage></Coverage>
    <ContinuityOfCare></ContinuityOfCare>
    {_build_patient_section(patient_data)}
  </PrescriptionRequest>
</PatientRequest>"""

    # Print the complete XML template for debugging
    log.info("=" * 80)
    log.info("PDMP-XMLMapper: COMPLETE XML TEMPLATE")
    log.info("=" * 80)
    log.info(xml_template)
    log.info("=" * 80)
    log.info("PDMP-XMLMapper: END XML TEMPLATE")
    log.info("=" * 80)

    log.info(f"PDMP-XMLMapper: XML template created successfully ({len(xml_template)} characters)")
    return xml_template


def _build_provider_section(practitioner_data: Dict[str, Any]) -> str:
    """Build Provider XML section from practitioner data using real Canvas data."""
    # if not practitioner_data:   # TODO: remove this?
    #     log.warning(
    #         "PDMP-XMLMapper: No practitioner data available, creating minimal Provider section"
    #     )
    #     # TODO: Why defaulting to Physician
    #     return """<Provider>
    #   <Role>Physician</Role>
    #   <FirstName></FirstName>
    #   <LastName></LastName>
    # </Provider>"""

    log.info("PDMP-XMLMapper: Building Provider section from Canvas data")

    provider_xml = f"""<Provider>
      <Role>{practitioner_data.get("role", "Physician")}</Role>
      <FirstName>{practitioner_data.get("first_name", "")}</FirstName>
      <LastName>{practitioner_data.get("last_name", "")}</LastName>"""

    # Add middle name if available
    if practitioner_data.get("middle_name"):
        provider_xml += f"\n      <MiddleName>{practitioner_data['middle_name']}</MiddleName>"

    # Add DEA number if available
    if practitioner_data.get("dea_number"):
        provider_xml += f"\n      <DEANumber>{practitioner_data['dea_number']}</DEANumber>"

    # Add NPI number if available
    if practitioner_data.get("npi_number"):
        provider_xml += f"\n      <NPINumber>{practitioner_data['npi_number']}</NPINumber>"

    # Add professional license if available
    license_number = practitioner_data.get("license_number")
    license_type = practitioner_data.get("license_type")
    license_state = practitioner_data.get("license_state")

    if license_number and license_state:
        provider_xml += f"""
      <ProfessionalLicenseNumber>
        <Type>{license_type or "Medical"}</Type>
        <Value>{license_number}</Value>
        <StateCode>{license_state.upper()}</StateCode>
      </ProfessionalLicenseNumber>"""
    elif practitioner_data.get("npi_number"):
        # Fallback: use NPI as professional license if no license info available
        provider_xml += f"""
      <ProfessionalLicenseNumber>
        <Type>NPI</Type>
        <Value>{practitioner_data["npi_number"]}</Value>
        <StateCode>{_get_pmp_destination({})} </StateCode>
      </ProfessionalLicenseNumber>"""

    provider_xml += "\n    </Provider>"
    return provider_xml


def _build_location_section(organization_data: Dict[str, Any]) -> str:
    """Build Location XML section from organization data using real Canvas data."""
    log.info("PDMP-XMLMapper: Building Location section from Canvas data")

    practice_location = organization_data.get("practice_location", {})
    org_name = organization_data.get("name", "")
    location_name = practice_location.get("name") or org_name or "Unknown Location"

    location_xml = f"""<Location>
      <Name>{location_name}</Name>"""

    # Add organization NPI if available
    if organization_data.get("group_npi"):
        location_xml += f"\n      <NPINumber>{organization_data['group_npi']}</NPINumber>"
    # Add practice location NPI if available
    elif practice_location.get("npi"):
        location_xml += f"\n      <NPINumber>{practice_location['npi']}</NPINumber>"

    # Add DEA number if available at practice location
    # if practice_location.get("dea"):
    #     location_xml += f"\n      <DEANumber>{practice_location['dea']}</DEANumber>"

    # Add NCPDP number if available at practice location
    if practice_location.get("ncpdp"):
        location_xml += f"\n      <NCPDPNumber>{practice_location['ncpdp']}</NCPDPNumber>"

    # Add address if available from practice location
    address = practice_location.get("address", {})
    if any(address.values()):
        location_xml += "\n      <Address>"

        if address.get("street"):
            location_xml += f"\n        <Street>{address['street']}</Street>"
        # if address.get("street2"):
        #     location_xml += f"\n        <Street2>{address['street2']}</Street2>"
        if address.get("city"):
            location_xml += f"\n        <City>{address['city']}</City>"
        if address.get("state"):
            location_xml += f"\n        <StateCode>{address['state'].upper()}</StateCode>"
        if address.get("zip_code"):
            location_xml += f"\n        <ZipCode>{address['zip_code']}</ZipCode>"
        if address.get("zip_plus_four"):
            location_xml += f"\n        <ZipPlusFour>{address['zip_plus_four']}</ZipPlusFour>"

        location_xml += "\n      </Address>"

    location_xml += "\n    </Location>"
    return location_xml


def _build_patient_section(patient_data: Dict[str, Any]) -> str:
    """Build Patient XML section from patient data using real Canvas data."""
    if not patient_data:
        log.warning("PDMP-XMLMapper: No patient data available, creating minimal Patient section")
        return """<Patient>
      <Name>
        <First></First>
        <Last></Last>
      </Name>
      <Birthdate></Birthdate>
      <SexCode>U</SexCode>
    </Patient>"""

    log.info("PDMP-XMLMapper: Building Patient section from Canvas data")

    address_data = patient_data.get("address", {})

    patient_xml = f"""<Patient>
      <Name>
        <First>{patient_data.get("first_name", "")}</First>"""

    # Add middle name if available
    if patient_data.get("middle_name"):
        patient_xml += f"\n        <Middle>{patient_data['middle_name']}</Middle>"

    patient_xml += f"""
        <Last>{patient_data.get("last_name", "")}</Last>
      </Name>
      <Birthdate>{patient_data.get("birth_date", "")}</Birthdate>
      <SexCode>{patient_data.get("sex", "U")}</SexCode>"""

    # Add address if available from Canvas patient data
    if any(address_data.values()):
        patient_xml += "\n      <Address>"

        if address_data.get("street"):
            patient_xml += f"\n        <Street>{address_data['street']}</Street>"
        if address_data.get("street2"):
            patient_xml += f"\n        <Street>{address_data['street2']}</Street>"
        if address_data.get("city"):
            patient_xml += f"\n        <City>{address_data['city']}</City>"
        if address_data.get("state"):
            patient_xml += f"\n        <StateCode>{address_data['state'].upper()}</StateCode>"
        if address_data.get("zip_code"):
            patient_xml += f"\n        <ZipCode>{address_data['zip_code']}</ZipCode>"

        patient_xml += "\n      </Address>"

    # Add phone if available
    if patient_data.get("phone"):
        patient_xml += f"\n      <Phone>{patient_data['phone']}</Phone>"

    # Add SSN if available
    if patient_data.get("ssn"):
        patient_xml += f"\n      <SSN>{patient_data['ssn']}</SSN>"

    # Add MRN if available
    if patient_data.get("mrn"):
        patient_xml += f"\n      <MedicalRecordID>{patient_data['mrn']}</MedicalRecordID>"

    patient_xml += "\n    </Patient>"
    return patient_xml


def create_report_request_xml(canvas_data: Dict[str, Any]) -> str:
    """
    Create ReportRequest XML using Canvas data.
    This ensures the ReportRequest uses the same provider/location data as the PatientRequest.
    """
    log.info("PDMP-XMLMapper: Creating dynamic ReportRequest XML")

    # Validate and fill missing data
    validated_data = _validate_patient_request_data(canvas_data)

    if not validated_data["valid"]:
        error_msg = f"PDMP-XMLMapper: Cannot create ReportRequest XML due to validation errors: {', '.join(validated_data['errors'])}"
        log.error(error_msg)
        raise ValueError(error_msg)

    # Extract validated data
    practitioner_data = validated_data["data"].get("practitioner", {})
    organization_data = validated_data["data"].get("organization", {})

    log.info("PDMP-XMLMapper: Extracted data for ReportRequest:")
    log.info(f"  Practitioner data: {practitioner_data}")
    log.info(f"  Organization data: {organization_data}")

    # Build provider section (use actual role from practitioner data)
    provider_first = practitioner_data.get("first_name", "Jon")
    provider_last = practitioner_data.get("last_name", "Doe")
    provider_dea = practitioner_data.get("dea_number", "AB1234579")
    provider_role = practitioner_data.get("role", "Physician")  # Use actual role with fallback

    # Build location section (use practice_location data)
    practice_location = organization_data.get("practice_location", {})
    location_name = practice_location.get("name", "Canvas Test Site")
    location_dea = practice_location.get("dea", "AB1234579")
    location_npi = practice_location.get("npi", "0123456789")
    location_state = practice_location.get("address", {}).get("state", "KS")

    log.info("PDMP-XMLMapper: Provider section data:")
    log.info(f"  Role: {provider_role}")
    log.info(f"  First Name: {provider_first}")
    log.info(f"  Last Name: {provider_last}")
    log.info(f"  DEA Number: {provider_dea}")

    log.info("PDMP-XMLMapper: Location section data:")
    log.info(f"  Name: {location_name}")
    log.info(f"  DEA Number: {location_dea}")
    log.info(f"  NPI Number: {location_npi}")
    log.info(f"  State Code: {location_state}")

    # Create XML
    report_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ReportRequest xmlns="http://xml.appriss.com/gateway/v5_1">
  <Requester>
    <Provider>
      <Role>{provider_role}</Role>
      <FirstName>{provider_first}</FirstName>
      <LastName>{provider_last}</LastName>
      <DEANumber>{provider_dea}</DEANumber>
    </Provider>
    <Location>
      <Name>{location_name}</Name>
      <DEANumber>{location_dea}</DEANumber>
      <NPINumber>{location_npi}</NPINumber>
      <Address>
        <StateCode>{location_state}</StateCode>
      </Address>
    </Location>
  </Requester>
</ReportRequest>"""

    log.info(f"PDMP-XMLMapper: Created ReportRequest XML ({len(report_xml)} characters)")
    return report_xml


# HELPER FUNCTION TO CREATE A VALID REQUEST!
# def _validate_and_fill_minimal_fields(canvas_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Validate that we have the minimal required fields for a successful PDMP request.
#     If missing, fill with hardcoded test data that we know works.
#
#     Returns:
#         Dict with validated and filled data
#     """
#     log.info("PDMP-XMLMapper: Validating minimal required fields for PDMP request")
#
#     # Extract data
#     patient_data = canvas_data.get("patient", {})
#     practitioner_data = canvas_data.get("practitioner", {})
#     organization_data = canvas_data.get("organization", {})
#
#     # Track what we're filling with test data
#     filled_fields = []
#
#     # Validate and fill patient data
#     if not patient_data.get("first_name") or not patient_data.get("last_name"):
#         log.warning("PDMP-XMLMapper: Missing patient name, using test data")
#         patient_data["first_name"] = "Alice"
#         patient_data["last_name"] = "Testpatient"
#         filled_fields.append("patient_name")
#
#     if not patient_data.get("birth_date"):
#         log.warning("PDMP-XMLMapper: Missing patient birth date, using test data")
#         patient_data["birth_date"] = "1950-01-01"
#         filled_fields.append("patient_birth_date")
#
#     if not patient_data.get("address", {}).get("zip_code"):
#         log.warning("PDMP-XMLMapper: Missing patient zip code, using test data")
#         if "address" not in patient_data:
#             patient_data["address"] = {}
#         patient_data["address"]["zip_code"] = "67203"
#         filled_fields.append("patient_zip")
#
#     # Validate and fill practitioner data
#     if not practitioner_data.get("first_name") or not practitioner_data.get("last_name"):
#         log.warning("PDMP-XMLMapper: Missing practitioner name, using test data")
#         practitioner_data["first_name"] = "Jon"
#         practitioner_data["last_name"] = "Doe"
#         filled_fields.append("practitioner_name")
#
#     if not practitioner_data.get("dea_number"):
#         log.warning("PDMP-XMLMapper: Missing practitioner DEA number, using test data")
#         practitioner_data["dea_number"] = "AB1234579"
#         filled_fields.append("practitioner_dea")
#
#     # Validate and fill organization data
#     if not organization_data.get("name"):
#         log.warning("PDMP-XMLMapper: Missing organization name, using test data")
#         organization_data["name"] = "Canvas Test Site"
#         filled_fields.append("organization_name")
#
#     if not organization_data.get("dea_number"):
#         log.warning("PDMP-XMLMapper: Missing organization DEA number, using test data")
#         organization_data["dea_number"] = "AB1234579"
#         filled_fields.append("organization_dea")
#
#     if not organization_data.get("npi_number"):
#         log.warning("PDMP-XMLMapper: Missing organization NPI number, using test data")
#         organization_data["npi_number"] = "0123456789"
#         filled_fields.append("organization_npi")
#
#     if not organization_data.get("address", {}).get("state_code"):
#         log.warning("PDMP-XMLMapper: Missing organization state, using test data")
#         if "address" not in organization_data:
#             organization_data["address"] = {}
#         organization_data["address"]["state_code"] = "KS"
#         filled_fields.append("organization_state")
#
#     # Log what we filled
#     if filled_fields:
#         log.warning(f"PDMP-XMLMapper: Filled {len(filled_fields)} fields with test data: {', '.join(filled_fields)}")
#         log.warning("PDMP-XMLMapper: This request will use hardcoded test data for missing fields")
#     else:
#         log.info("PDMP-XMLMapper: All required fields present, using real Canvas data")
#
#     # Return updated data
#     return {
#         "patient": patient_data,
#         "practitioner": practitioner_data,
#         "organization": organization_data
#     }