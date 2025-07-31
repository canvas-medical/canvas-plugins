"""
XML Payload Generation for PMP Gateway
"""

import uuid
from typing import Dict, Any, Optional


class PMPGatewayXMLGenerator:
    """Generates the XML payload for the PMP Gateway request."""

    @staticmethod
    def _xml_escape(text: str) -> str:
        """Escapes special characters for safe inclusion in XML."""
        if not text:
            return ""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    @staticmethod
    def _add_element(name: str, value: str, indent: str = "      ") -> str:
        """Add XML element only if value is present."""
        if value:
            escaped_value = PMPGatewayXMLGenerator._xml_escape(value)
            return f"{indent}<{name}>{escaped_value}</{name}>\n"
        return ""

    @staticmethod
    def _get_safe(data: Dict[str, Any], key: str) -> str:
        """Safely get value from dict, return empty string if not present."""
        return str(data.get(key, "")) if data.get(key) else ""

    @staticmethod
    def generate_patient_request_xml(
        patient_data: Dict[str, Any], staff_data: Dict[str, Any], location_config: Dict[str, str]
    ) -> str:
        """
        Generates the XML payload for a patient PDMP request.
        Only includes data that is actually present - no defaults.

        TODO: For production use, ensure all required fields are validated
        before calling this method. Missing data will result in API errors.
        """
        request_id = f"test-{uuid.uuid4()}"

        # Provider section - only include fields that are present
        provider_xml = ""
        if staff_data:
            provider_xml += PMPGatewayXMLGenerator._add_element(
                "Role", PMPGatewayXMLGenerator._get_safe(staff_data, "role")
            )
            provider_xml += PMPGatewayXMLGenerator._add_element(
                "FirstName", PMPGatewayXMLGenerator._get_safe(staff_data, "first_name")
            )
            provider_xml += PMPGatewayXMLGenerator._add_element(
                "LastName", PMPGatewayXMLGenerator._get_safe(staff_data, "last_name")
            )
            provider_xml += PMPGatewayXMLGenerator._add_element(
                "DEANumber", PMPGatewayXMLGenerator._get_safe(staff_data, "dea_number")
            )
            provider_xml += PMPGatewayXMLGenerator._add_element(
                "NPINumber", PMPGatewayXMLGenerator._get_safe(staff_data, "npi_number")
            )

        # Location section - only include fields that are present
        location_xml = ""
        location_address_xml = ""
        if location_config:
            location_xml += PMPGatewayXMLGenerator._add_element(
                "Name", PMPGatewayXMLGenerator._get_safe(location_config, "name")
            )
            location_xml += PMPGatewayXMLGenerator._add_element(
                "DEANumber", PMPGatewayXMLGenerator._get_safe(location_config, "dea")
            )
            location_xml += PMPGatewayXMLGenerator._add_element(
                "NPINumber", PMPGatewayXMLGenerator._get_safe(location_config, "npi")
            )

            # Location address if present
            if any(location_config.get(k) for k in ["street", "city", "state", "zip_code"]):
                location_address_xml = "      <Address>\n"
                location_address_xml += PMPGatewayXMLGenerator._add_element(
                    "Street",
                    PMPGatewayXMLGenerator._get_safe(location_config, "street"),
                    "        ",
                )
                location_address_xml += PMPGatewayXMLGenerator._add_element(
                    "City", PMPGatewayXMLGenerator._get_safe(location_config, "city"), "        "
                )
                location_address_xml += PMPGatewayXMLGenerator._add_element(
                    "StateCode",
                    PMPGatewayXMLGenerator._get_safe(location_config, "state"),
                    "        ",
                )
                location_address_xml += PMPGatewayXMLGenerator._add_element(
                    "ZipCode",
                    PMPGatewayXMLGenerator._get_safe(location_config, "zip_code"),
                    "        ",
                )
                location_address_xml += "      </Address>\n"

        # Patient name section
        patient_name_xml = ""
        if patient_data:
            first_name = PMPGatewayXMLGenerator._get_safe(patient_data, "first_name")
            last_name = PMPGatewayXMLGenerator._get_safe(patient_data, "last_name")
            if first_name or last_name:
                patient_name_xml = "        <Name>\n"
                patient_name_xml += PMPGatewayXMLGenerator._add_element(
                    "First", first_name, "          "
                )
                patient_name_xml += PMPGatewayXMLGenerator._add_element(
                    "Last", last_name, "          "
                )
                patient_name_xml += "        </Name>\n"

        # Patient demographics - only include if present
        patient_demo_xml = ""
        if patient_data:
            patient_demo_xml += PMPGatewayXMLGenerator._add_element(
                "Birthdate", PMPGatewayXMLGenerator._get_safe(patient_data, "dob"), "      "
            )
            patient_demo_xml += PMPGatewayXMLGenerator._add_element(
                "SexCode", PMPGatewayXMLGenerator._get_safe(patient_data, "sex"), "      "
            )

        # Patient address - REQUIRED by PMP Gateway (must have Address OR Phone)
        patient_address_xml = ""
        if patient_data and patient_data.get("address"):
            address_data = patient_data["address"]
            # If we have any address data, include it
            if any(address_data.get(k) for k in ["street", "city", "state", "zip_code"]):
                patient_address_xml = "      <Address>\n"
                patient_address_xml += PMPGatewayXMLGenerator._add_element(
                    "Street", PMPGatewayXMLGenerator._get_safe(address_data, "street"), "        "
                )
                patient_address_xml += PMPGatewayXMLGenerator._add_element(
                    "City", PMPGatewayXMLGenerator._get_safe(address_data, "city"), "        "
                )
                patient_address_xml += PMPGatewayXMLGenerator._add_element(
                    "StateCode", PMPGatewayXMLGenerator._get_safe(address_data, "state"), "        "
                )
                patient_address_xml += PMPGatewayXMLGenerator._add_element(
                    "ZipCode",
                    PMPGatewayXMLGenerator._get_safe(address_data, "zip_code"),
                    "        ",
                )
                patient_address_xml += "      </Address>\n"

        # If no address data available, include minimal Address to satisfy API requirements
        if not patient_address_xml:
            patient_address_xml = "      <Address>\n"
            patient_address_xml += "        <Street></Street>\n"
            patient_address_xml += "        <City></City>\n"
            patient_address_xml += "        <StateCode></StateCode>\n"
            patient_address_xml += "        <ZipCode></ZipCode>\n"
            patient_address_xml += "      </Address>\n"

        # Build the complete XML
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatientRequest xmlns="http://xml.appriss.com/gateway/v5_1">
  <Requester>
    <LicenseeRequestId>{request_id}</LicenseeRequestId>
    <SenderSoftware>
      <Developer>Canvas Medical</Developer>
      <Product>Canvas PDMP Plugin</Product>
      <Version>1.0</Version>
    </SenderSoftware>
    <Provider>
{provider_xml.rstrip()}
    </Provider>
    <Location>
{location_xml.rstrip()}
{location_address_xml.rstrip()}
    </Location>
  </Requester>
  <PrescriptionRequest>
    <Patient>
{patient_name_xml.rstrip()}
{patient_demo_xml.rstrip()}
{patient_address_xml.rstrip()}
    </Patient>
  </PrescriptionRequest>
</PatientRequest>"""

        return xml

    @staticmethod
    def generate_patient_request_xml_for_testing(
        patient_data: Optional[Dict[str, Any]] = None,
        staff_data: Optional[Dict[str, Any]] = None,
        location_config: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generates XML with default test values for testing purposes only.
        Uses the same values that work with bamboo_request.py.

        TODO: Remove this method in production - only use generate_patient_request_xml
        """
        # Default test data that matches bamboo_request.py
        test_patient = patient_data or {
            "first_name": "John",
            "last_name": "TestPatient",
            "dob": "1985-05-15",
            "sex": "M",
            "address": {
                "street": "123 Main St",
                "city": "Test City",
                "state": "KS",
                "zip_code": "67203",
            },
        }

        test_staff = staff_data or {
            "role": "Physician",
            "first_name": "Test",
            "last_name": "Provider",
            "dea_number": "AB1234579",
            "npi_number": "1212345671",
        }

        test_location = location_config or {
            "name": "Test Clinic",
            "dea": "AB1234579",
            "npi": "1234567890",
            "state": "KS",
            "street": "123 Test St",
            "city": "Test City",
            "zip_code": "67203",
        }

        return PMPGatewayXMLGenerator.generate_patient_request_xml(
            test_patient, test_staff, test_location
        )
