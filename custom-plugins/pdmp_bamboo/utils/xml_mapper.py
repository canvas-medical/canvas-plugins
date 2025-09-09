"""
XML Template Mapping Utility for PDMP Requests

This module provides functionality to map Canvas data to PDMP XML template
for BambooHealth PMP Gateway requests using real extracted data.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
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
    return "KS"


def create_pdmp_xml(canvas_data: Dict[str, Any]) -> str:
    """
    Create PDMP XML request from Canvas data.

    Args:
        canvas_data: Dictionary containing Canvas patient, practitioner, and organization data

    Returns:
        XML string formatted for PDMP request
    """
    log.info("PDMP-XMLMapper: Starting PDMP XML creation from Canvas data")

    patient_data = canvas_data.get("patient", {})
    practitioner_data = canvas_data.get("practitioner", {})
    organization_data = canvas_data.get("organization", {})

    # Generate unique request ID
    request_id = str(uuid.uuid4())

    # Get dynamic date range
    date_range = _get_dynamic_date_range()

    # Get PMP destination from organization data
    pmp_destination = _get_pmp_destination(organization_data)

    log.info(f"PDMP-XMLMapper: Generated request ID: {request_id}")
    log.info(f"PDMP-XMLMapper: Using date range: {date_range['begin']} to {date_range['end']}")
    log.info(f"PDMP-XMLMapper: Using PMP destination: {pmp_destination}")
    log.info(
        f"PDMP-XMLMapper: Mapping patient: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"
    )
    log.info(
        f"PDMP-XMLMapper: Mapping practitioner: {practitioner_data.get('first_name', '')} {practitioner_data.get('last_name', '')}"
    )
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

    log.info(f"PDMP-XMLMapper: XML template created successfully ({len(xml_template)} characters)")
    return xml_template


def _build_provider_section(practitioner_data: Dict[str, Any]) -> str:
    """Build Provider XML section from practitioner data using real Canvas data."""
    if not practitioner_data:
        log.warning(
            "PDMP-XMLMapper: No practitioner data available, creating minimal Provider section"
        )
        return """<Provider>
      <Role>Physician</Role>
      <FirstName></FirstName>
      <LastName></LastName>
    </Provider>"""

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
    if not organization_data:
        log.warning(
            "PDMP-XMLMapper: No organization data available, creating minimal Location section"
        )
        return """<Location>
      <Name>Unknown Location</Name>
    </Location>"""

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
    if practice_location.get("dea"):
        location_xml += f"\n      <DEANumber>{practice_location['dea']}</DEANumber>"

    # Add NCPDP number if available at practice location
    if practice_location.get("ncpdp"):
        location_xml += f"\n      <NCPDPNumber>{practice_location['ncpdp']}</NCPDPNumber>"

    # Add address if available from practice location
    address = practice_location.get("address", {})
    if any(address.values()):
        location_xml += "\n      <Address>"

        if address.get("street"):
            location_xml += f"\n        <Street>{address['street']}</Street>"
        if address.get("street2"):
            location_xml += f"\n        <Street>{address['street2']}</Street>"
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
