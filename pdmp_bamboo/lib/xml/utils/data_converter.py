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

    def _convert_patient_dto(self, patient_dto) -> dict[str, Any]:
        """Convert PatientDTO to XML format."""
        if not patient_dto:
            log.warning("DTOToXMLConverter: No patient DTO provided")
            return {}

        log.debug(f"DTOToXMLConverter: Converting patient DTO: {patient_dto.__dict__}")

        return {
            "first_name": patient_dto.first_name,
            "last_name": patient_dto.last_name,
            "middle_name": patient_dto.middle_name,
            "birth_date": patient_dto.birth_date,
            "sex": patient_dto.sex,
            "mrn": patient_dto.mrn,
            "ssn": patient_dto.ssn,
            "phone": patient_dto.phone,
            "address": self._convert_address_dto(patient_dto.address),
        }

    def _convert_practitioner_dto(self, practitioner_dto) -> dict[str, Any]:
        """Convert PractitionerDTO to XML format."""
        if not practitioner_dto:
            log.warning("DTOToXMLConverter: No practitioner DTO provided")
            return {}

        log.debug(f"DTOToXMLConverter: Converting practitioner DTO: {practitioner_dto.__dict__}")

        return {
            "first_name": practitioner_dto.first_name,
            "last_name": practitioner_dto.last_name,
            "middle_name": practitioner_dto.middle_name,
            "npi_number": practitioner_dto.npi_number,
            "dea_number": practitioner_dto.dea_number,
            "role": practitioner_dto.role,
            "phone": practitioner_dto.phone,
            "email": practitioner_dto.email,
            "active": practitioner_dto.active,
            "license_number": practitioner_dto.license_number,
            "license_type": practitioner_dto.license_type,
            "license_state": practitioner_dto.license_state,
            "organization_id": practitioner_dto.organization_id,
            "organization_name": practitioner_dto.organization_name,
            "practice_location_id": practitioner_dto.practice_location_id,
            "practice_location_name": practitioner_dto.practice_location_name,
        }

    def _convert_organization_dto(self, organization_dto) -> dict[str, Any]:
        """Convert OrganizationDTO to XML format."""
        if not organization_dto:
            log.warning("DTOToXMLConverter: No organization DTO provided")
            return {}

        log.debug(f"DTOToXMLConverter: Converting organization DTO: {organization_dto.__dict__}")

        return {
            "id": organization_dto.id,
            "name": organization_dto.name,
            "active": organization_dto.active,
            "group_npi": getattr(organization_dto, "group_npi", ""),
        }

    def _convert_practice_location_dto(self, practice_location_dto) -> dict[str, Any]:
        """Convert PracticeLocationDTO to XML format."""
        if not practice_location_dto:
            log.warning("DTOToXMLConverter: No practice location DTO provided")
            return {}

        log.debug(
            f"DTOToXMLConverter: Converting practice location DTO: {practice_location_dto.__dict__}"
        )

        return {
            "id": practice_location_dto.id,
            "name": practice_location_dto.name,
            "npi": practice_location_dto.npi,
            "dea": practice_location_dto.dea,
            "ncpdp": practice_location_dto.ncpdp,
            "phone": practice_location_dto.phone,
            "active": practice_location_dto.active,
            "address": self._convert_address_dto(practice_location_dto.address),
        }

    def _convert_address_dto(self, address_dto) -> dict[str, Any]:
        """Convert AddressDTO to XML format."""
        if not address_dto:
            return {}

        return {
            "street": address_dto.street,
            "street2": address_dto.street2,
            "city": address_dto.city,
            "state": address_dto.state,
            "zip_code": address_dto.zip_code,
            "zip_plus_four": address_dto.zip_plus_four,
        }

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
