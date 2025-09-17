"""
Request XML Builder

Builds the complete PDMP XML request by combining all sections.
"""

from typing import Dict, Any
from pdmp_bamboo.xml.builders.base_builder import BaseXMLBuilder
from logger import log


class RequestXMLBuilder(BaseXMLBuilder):
    """Builds complete PDMP XML requests."""

    def build(self, data: Dict[str, Any]) -> str:
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
        request_metadata = data.get("request_metadata", {})

        # Build the complete XML request
        xml_request = self._build_complete_request(
            patient_xml,
            practitioner_xml,
            location_xml,
            request_metadata
        )

        log.info("RequestXMLBuilder: Complete PDMP XML request built successfully")
        return xml_request

    def _build_complete_request(self,
                                patient_xml: str,
                                practitioner_xml: str,
                                location_xml: str,
                                request_metadata: Dict[str, Any]) -> str:
        """Build the complete PDMP XML request."""

        # Get request metadata
        timestamp = request_metadata.get("timestamp", "")
        request_id = request_metadata.get("request_id", "")

        # Build the complete XML structure with correct v5.1 schema
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