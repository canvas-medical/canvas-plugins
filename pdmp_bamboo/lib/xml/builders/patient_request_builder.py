"""
Request XML Builder.

Builds the complete PDMP XML request by combining all sections.
"""

from typing import Any

from logger import log
from pdmp_bamboo.lib.xml.builders.base_builder import BaseXMLBuilder


class PatientRequestXMLBuilder(BaseXMLBuilder):
    """Builds complete PDMP XML requests."""

    def build(self, data: dict[str, Any]) -> str:
        """
        Build complete PDMP XML request.

        Args:
            data: Dictionary containing:
                - patient_xml: Patient section XML
                - practitioner_xml: Practitioner section XML
                - location_xml: Location section XML
                - request_metadata: Request metadata (timestamp, etc.)

        Returns:
            Complete PDMP XML request
        """
        log.info("RequestXMLBuilder: Building complete PDMP XML request")

        # Extract data from the input dictionary
        patient_xml = data.get("patient_xml", "")
        practitioner_xml = data.get("practitioner_xml", "")
        location_xml = data.get("location_xml", "")

        # Build the complete XML request
        xml_request = self._build_complete_request(patient_xml, practitioner_xml, location_xml)

        log.info("RequestXMLBuilder: Complete PDMP XML request built successfully")
        return xml_request

    def _build_complete_request(
        self, patient_xml: str, practitioner_xml: str, location_xml: str
    ) -> str:
        """Build the complete PDMP XML request."""
        xml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
    <PatientRequest xmlns="http://xml.appriss.com/gateway/v5_1">
        <Requester>
            {practitioner_xml}
            {location_xml}
        </Requester>
        <PrescriptionRequest>
            {patient_xml}
        </PrescriptionRequest>
    </PatientRequest>"""

        return xml_request
