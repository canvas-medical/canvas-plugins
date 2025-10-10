"""
DTO to XML Data Converter.

Converts DTOs to XML-friendly dictionary format.
"""

from typing import Any

from logger import log


class DTOToXMLConverter:
    """Converts DTOs to XML-friendly format."""

    def convert_to_xml_format(self, extracted_data: dict) -> dict:
        """Convert DTOs to dictionary format expected by XML builders."""
        log.info("DTOToXMLConverter: Converting extracted data to XML format")

        return {
            "patient": self._convert_patient_dto(extracted_data.get("patient")),
            "practitioner": self._convert_practitioner_dto(extracted_data.get("practitioner")),
            "organization": self._convert_organization_dto(extracted_data.get("organization")),
            "practice_location": self._convert_practice_location_dto(
                extracted_data.get("practice_location")
            ),
            "metadata": self._build_request_metadata(extracted_data),
        }

    def _convert_dto(self, dto, dto_name: str) -> dict[str, Any]:
        """
        Generic DTO conversion with consistent logging.
        
        Now that DTOs are dataclasses, conversion is simple via to_dict().
        
        Args:
            dto: DTO instance to convert
            dto_name: Name of DTO for logging
            
        Returns:
            Dictionary representation of DTO
        """
        if not dto:
            log.warning(f"DTOToXMLConverter: No {dto_name} DTO provided")
            return {}

        log.debug(f"DTOToXMLConverter: Converting {dto_name} DTO")

        # DTOs now have to_dict() via dataclass asdict()
        return dto.to_dict() if hasattr(dto, "to_dict") else {}

    def _convert_patient_dto(self, patient_dto) -> dict[str, Any]:
        """Convert PatientDTO to XML format."""
        return self._convert_dto(patient_dto, "patient")

    def _convert_practitioner_dto(self, practitioner_dto) -> dict[str, Any]:
        """Convert PractitionerDTO to XML format."""
        result = self._convert_dto(practitioner_dto, "practitioner")
        # Add group_npi if not present (for backward compatibility)
        if result and "group_npi" not in result:
            result["group_npi"] = ""
        return result

    def _convert_organization_dto(self, organization_dto) -> dict[str, Any]:
        """Convert OrganizationDTO to XML format."""
        result = self._convert_dto(organization_dto, "organization")
        # Add group_npi if not present (for backward compatibility)
        if result and "group_npi" not in result:
            result["group_npi"] = ""
        return result

    def _convert_practice_location_dto(self, practice_location_dto) -> dict[str, Any]:
        """Convert PracticeLocationDTO to XML format."""
        return self._convert_dto(practice_location_dto, "practice_location")

    def _build_request_metadata(self, extracted_data: dict) -> dict[str, Any]:
        """Build request metadata for XML generation."""
        # Determine PMP destination from practice location state
        practice_location = extracted_data.get("practice_location")
        pmp_destination = ""  # Default

        if practice_location and hasattr(practice_location, "address"):
            address = practice_location.address
            if address and address.state:
                pmp_destination = address.state.upper()
                log.info(
                    f"DTOToXMLConverter: Using PMP destination from practice location: {pmp_destination}"
                )

        return {
            "pmp_destination": pmp_destination,
            "request_timestamp": None,  # Will be set by request builder
            "extraction_errors": extracted_data.get("extraction_errors", []),
        }
