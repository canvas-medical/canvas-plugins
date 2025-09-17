"""
Report Request XML Builder

Builds ReportRequest XML for fetching specific PDMP reports.
This is different from the main PDMPRequest XML used for patient queries.
"""

from typing import Dict, Any
from pdmp_bamboo.xml.builders.base_builder import BaseXMLBuilder
from logger import log


class ReportRequestXMLBuilder(BaseXMLBuilder):
    """Builds ReportRequest XML for PDMP report fetching."""

    def build(self, data: Dict[str, Any]) -> str:
        """
        Build ReportRequest XML from extracted data.

        Args:
            data: Dictionary containing:
                - practitioner: Practitioner data
                - organization: Organization data
                - practice_location: Practice location data

        Returns:
            ReportRequest XML string
        """
        log.info("ReportRequestXMLBuilder: Building ReportRequest XML")
        log.info(f"ReportRequestXMLBuilder: Input data keys: {list(data.keys())}")

        # Log the input data structure
        for key, value in data.items():
            if isinstance(value, dict):
                log.info(f"ReportRequestXMLBuilder: {key} data fields: {list(value.keys())}")
            else:
                log.info(f"ReportRequestXMLBuilder: {key} data type: {type(value)}")

        # Extract data
        practitioner_data = data.get("practitioner", {})
        organization_data = data.get("organization", {})
        practice_location_data = data.get("practice_location", {})

        log.info("ReportRequestXMLBuilder: Extracted data:")
        log.info(f"  - Practitioner fields: {list(practitioner_data.keys())}")
        log.info(f"  - Organization fields: {list(organization_data.keys())}")
        log.info(f"  - Practice location fields: {list(practice_location_data.keys())}")

        # Build the ReportRequest XML
        xml_request = self._build_report_request(
            practitioner_data,
            organization_data,
            practice_location_data
        )

        log.info("ReportRequestXMLBuilder: ReportRequest XML built successfully")
        log.info(f"ReportRequestXMLBuilder: XML length: {len(xml_request)} characters")

        # Log the complete XML for debugging
        log.info("=" * 80)
        log.info("ReportRequestXMLBuilder: COMPLETE REPORT REQUEST XML:")
        log.info("=" * 80)
        log.info(xml_request)
        log.info("=" * 80)

        return xml_request

    def _build_report_request(self,
                              practitioner_data: Dict[str, Any],
                              organization_data: Dict[str, Any],
                              practice_location_data: Dict[str, Any]) -> str:
        """Build the complete ReportRequest XML with proper v5.1 schema."""

        # Extract practitioner info
        provider_first = practitioner_data.get("first_name", "Jon")
        provider_last = practitioner_data.get("last_name", "Doe")
        provider_dea = practitioner_data.get("dea_number", "AB1234579")
        provider_role = practitioner_data.get("role", "Physician")
        provider_npi = practitioner_data.get("npi_number", "")

        log.info(f"ReportRequestXMLBuilder: Practitioner data:")
        log.info(f"  - First name: {provider_first}")
        log.info(f"  - Last name: {provider_last}")
        log.info(f"  - DEA number: {provider_dea}")
        log.info(f"  - NPI number: {provider_npi}")
        log.info(f"  - Role: {provider_role}")

        # Extract location info
        location_name = practice_location_data.get("name", "Canvas Test Site")
        location_dea = practice_location_data.get("dea", "")
        location_npi = practice_location_data.get("npi", "0123456789")  # TODO: HARDCODED

        # Handle nested address data
        address_data = practice_location_data.get("address", {})
        if isinstance(address_data, dict):
            location_state = address_data.get("state", "KS")
            log.info(f"ReportRequestXMLBuilder: Address data: {address_data}")
        else:
            location_state = "KS"
            log.info(f"ReportRequestXMLBuilder: Address data is not a dict: {type(address_data)}")

        log.info(f"ReportRequestXMLBuilder: Location data:")
        log.info(f"  - Name: {location_name}")
        log.info(f"  - DEA: {location_dea}")
        log.info(f"  - NPI: {location_npi}")
        log.info(f"  - State: {location_state}")

        # Build Provider section
        provider_section = f"""        <Provider>
                <Role>{provider_role}</Role>
                <FirstName>{provider_first}</FirstName>
                <LastName>{provider_last}</LastName>
                <DEANumber>{provider_dea}</DEANumber>"""

        # Add NPI only if present
        if provider_npi:
            provider_section += f"""
                <NPINumber>{provider_npi}</NPINumber>"""

        provider_section += """
            </Provider>"""

        # Build Location section - Use NPINumber to match PatientRequest
        location_section = f"""        <Location>
                <Name>{location_name}</Name>"""

        # Add DEA only if present (don't send empty DEANumber)
        if location_dea:
            location_section += f"""
                <DEANumber>{location_dea}</DEANumber>"""

        # Use NPINumber instead of NCPDPNumber to match PatientRequest
        location_section += f"""
                <NPINumber>{location_npi}</NPINumber>
                <Address>
                    <StateCode>{location_state}</StateCode>
                </Address>
            </Location>"""

        # Build the complete XML with proper v5.1 schema
        xml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
    <ReportRequest xmlns="http://xml.appriss.com/gateway/v5_1">
        <Requester>
    {provider_section}
    {location_section}
        </Requester>
    </ReportRequest>"""

        return xml_request
