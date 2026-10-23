"""
XML Generation Service.

Main service for generating PDMP XML requests using the new modular architecture.
"""

from typing import Any

from logger import log

# Import our new XML components
from pdmp_bamboo.lib.xml.builders.location_builder import LocationXMLBuilder
from pdmp_bamboo.lib.xml.builders.patient_builder import PatientXMLBuilder
from pdmp_bamboo.lib.xml.builders.patient_request_builder import PatientRequestXMLBuilder
from pdmp_bamboo.lib.xml.builders.practitioner_builder import PractitionerXMLBuilder
from pdmp_bamboo.lib.xml.utils.data_converter import DTOToXMLConverter
from pdmp_bamboo.lib.xml.utils.xml_utils import XMLUtils


class XMLGenerationService:
    """Orchestrates XML generation using builders and validators."""

    def __init__(self):
        """Initialize the XML generation service with all required builders."""
        log.info("XMLGenerationService: Initializing XML generation service")

        # Initialize builders
        self.patient_builder = PatientXMLBuilder()
        self.practitioner_builder = PractitionerXMLBuilder()
        self.location_builder = LocationXMLBuilder()
        self.request_builder = PatientRequestXMLBuilder()

        # Initialize utilities
        self.data_converter = DTOToXMLConverter()
        self.xml_utils = XMLUtils()

        log.info("XMLGenerationService: XML generation service initialized successfully")

    def create_pdmp_xml(self, extracted_data: dict[str, Any]) -> str:
        """
        Main entry point for XML generation.

        Args:
            extracted_data: Dictionary containing extracted DTOs from data extraction service

        Returns:
            Complete PDMP XML request string

        Raises:
            ValueError: If data validation fails or required data is missing
        """
        log.info("XMLGenerationService: Starting PDMP XML generation")

        try:
            # Convert DTOs to XML-friendly format
            log.info("XMLGenerationService: Converting DTOs to XML format")
            xml_data = self.data_converter.convert_to_xml_format(extracted_data)

            # Log the converted data for debugging
            self.xml_utils.log_xml_data(xml_data)

            # Validate XML data structure
            if not self.xml_utils.validate_xml_data(xml_data):
                raise ValueError("Invalid XML data structure")

            # Validate required fields for XML generation
            validation_errors = self._validate_required_fields(xml_data)
            if validation_errors:
                error_msg = f"XML validation failed: {', '.join(validation_errors)}"
                log.error(f"XMLGenerationService: {error_msg}")
                raise ValueError(error_msg)

            # Build XML sections
            log.info("XMLGenerationService: Building XML sections")

            patient_xml = self.patient_builder.build(xml_data["patient"])
            practitioner_xml = self.practitioner_builder.build(xml_data["practitioner"])
            # Pass location data as a combined dictionary
            location_data = {
                "organization": xml_data["organization"],
                "practice_location": xml_data["practice_location"],
            }
            location_xml = self.location_builder.build(location_data)

            # Build complete request
            log.info("XMLGenerationService: Building complete XML request")
            request_data = {
                "patient_xml": patient_xml,
                "practitioner_xml": practitioner_xml,
                "location_xml": location_xml,
                "request_metadata": xml_data["metadata"],
            }
            complete_xml = self.request_builder.build(request_data)

            log.info(
                f"XMLGenerationService: XML generation completed successfully ({len(complete_xml)} characters)"
            )
            return complete_xml

        except Exception as e:
            log.error(f"XMLGenerationService: Error during XML generation: {str(e)}")
            raise

    def _validate_required_fields(self, xml_data: dict[str, Any]) -> list:
        """Validate that all required fields for XML generation are present."""
        errors = []

        # Validate patient data
        patient_data = xml_data.get("patient", {})
        if not patient_data.get("first_name"):
            errors.append("Patient first name is required")
        if not patient_data.get("last_name"):
            errors.append("Patient last name is required")
        if not patient_data.get("birth_date"):
            errors.append("Patient birth date is required")

        # Validate practitioner data
        practitioner_data = xml_data.get("practitioner", {})
        if not practitioner_data.get("first_name"):
            errors.append("Practitioner first name is required")
        if not practitioner_data.get("last_name"):
            errors.append("Practitioner last name is required")

        # At least one identifier is required
        if not practitioner_data.get("dea_number") and not practitioner_data.get("npi_number"):
            errors.append("Practitioner must have either DEA number or NPI number")

        # Validate practice location data
        practice_location_data = xml_data.get("practice_location", {})
        if not practice_location_data.get("name"):
            errors.append("Practice location name is required")
        if not practice_location_data.get("npi"):
            errors.append("Practice location NPI is required")

        # Address or NCPDP is required for practice location
        address_data = practice_location_data.get("address", {})
        has_address = any(address_data.values())
        has_ncpdp = bool(practice_location_data.get("ncpdp"))

        if not has_address and not has_ncpdp:
            errors.append("Practice location must have either address or NCPDP number")

        return errors
