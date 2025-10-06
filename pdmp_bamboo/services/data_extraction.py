from typing import List, Optional, Tuple, Dict, Any
from canvas_sdk.v1.data import Patient, Staff, Organization, PracticeLocation
from pdmp_bamboo.mappers.organization_mapper import OrganizationMapper
from pdmp_bamboo.mappers.patient_mapper import PatientMapper
from pdmp_bamboo.mappers.practice_location_mapper import PracticeLocationMapper
from pdmp_bamboo.mappers.practitioner_mapper import PractitionerMapper
from pdmp_bamboo.models.dtos import PatientDTO, PractitionerDTO, OrganizationDTO, PracticeLocationDTO
from pdmp_bamboo.utils.validators import PatientValidator, PractitionerValidator, OrganizationValidator, \
    PracticeLocationValidator
from logger import log


class DataExtractionService:
    """Service for extracting and validating data from Canvas models."""

    def __init__(self):
        self.practice_location_validator = PracticeLocationValidator()
        self.practice_location_mapper = PracticeLocationMapper()
        self.patient_mapper = PatientMapper()
        self.patient_validator = PatientValidator()
        self.practitioner_mapper = PractitionerMapper()
        self.practitioner_validator = PractitionerValidator()
        self.organization_mapper = OrganizationMapper()
        self.organization_validator = OrganizationValidator()

    def extract_patient(self, patient_id: str) -> Tuple[Optional[PatientDTO], list]:
        """Extract and validate patient data."""
        try:
            patient = Patient.objects.get(id=patient_id)
            patient_dto = self.patient_mapper.map_to_dto(patient)
            validation_errors = self.patient_validator.validate(patient_dto)
            patient_dto.errors = validation_errors
            if validation_errors:
                log.error(f"PDMP-DataExtractor: Patient validation errors: {validation_errors}")
            return patient_dto, validation_errors

        except Patient.DoesNotExist:
            return None, [f"Patient with ID '{patient_id}' not found"]
        except Exception as e:
            return None, [f"Error retrieving patient data: {str(e)}"]

    def extract_practitioner(self, practitioner_id: str) -> Tuple[Optional[PractitionerDTO], list]:
        """Extract and validate practitioner data."""
        if not practitioner_id:
            return None, ["Practitioner ID is required for PDMP request"]

        try:
            staff = Staff.objects.get(id=practitioner_id)
            practitioner_dto = self.practitioner_mapper.map_to_dto(staff)
            validation_errors = self.practitioner_validator.validate(practitioner_dto)
            practitioner_dto.errors = validation_errors
            if validation_errors:
                log.error(f"PDMP-DataExtractor: Practitioner validation errors: {validation_errors}")
            return practitioner_dto, validation_errors

        except Staff.DoesNotExist:
            return None, [f"Practitioner with ID '{practitioner_id}' not found"]
        except Exception as e:
            return None, [f"Error retrieving practitioner data: {str(e)}"]

    def extract_organization(self, organization_id: str) -> Tuple[Optional[OrganizationDTO], list]:
        """Extract and validate organization data."""
        try:
            # log.info(f"DataExtractionService: Getting organization with ID: {organization_id}")
            organization = Organization.objects.get(dbid=organization_id)
            # log.info(f"DataExtractionService: Organization found: {organization.full_name or organization.short_name}")

            # Create organization DTO (without practice location)
            organization_dto = OrganizationDTO(
                id=str(organization.dbid),
                name=organization.full_name or organization.short_name or "",
                active=getattr(organization, 'active', True),
                errors=[]
            )

            # log.info("DataExtractionService: Starting organization validation")
            validation_errors = self.organization_validator.validate(organization_dto)
            organization_dto.errors = validation_errors

            # log.info(
            #     f"DataExtractionService: Organization data extraction completed. Success: {bool(organization_dto)}, Errors: {len(validation_errors)}")
            # if validation_errors:
                # log.error(f"DataExtractionService: Organization validation errors: {validation_errors}")

            return organization_dto, validation_errors

        except Organization.DoesNotExist:
            error_msg = f"Organization with ID {organization_id} not found"
            # log.error(f"DataExtractionService: {error_msg}")
            return None, [error_msg]
        except Exception as e:
            error_msg = f"Error extracting organization data: {str(e)}"
            # log.error(f"DataExtractionService: {error_msg}")
            return None, [error_msg]

    def extract_practice_location(self, practice_location_id: str) -> Tuple[Optional[PracticeLocationDTO], list]:
        """Extract and validate practice location data."""
        try:
            # log.info(f"DataExtractionService: Getting practice location with ID: {practice_location_id}")
            practice_location = PracticeLocation.objects.get(id=practice_location_id)
            # log.info(f"DataExtractionService: Practice location found: {practice_location}")

            # Map practice location to DTO
            practice_location_dto = self.practice_location_mapper.map_to_dto(practice_location)

            # log.info("DataExtractionService: Starting practice location validation")
            validation_errors = self.practice_location_validator.validate(practice_location_dto)
            practice_location_dto.errors = validation_errors

            # log.info(
            #     f"DataExtractionService: Practice location data extraction completed. Success: {bool(practice_location_dto)}, Errors: {len(validation_errors)}")
            # if validation_errors:
                # log.error(f"DataExtractionService: Practice location validation errors: {validation_errors}")

            return practice_location_dto, validation_errors

        except PracticeLocation.DoesNotExist:
            error_msg = f"Practice location with ID {practice_location_id} not found"
            # log.error(f"DataExtractionService: {error_msg}")
            return None, [error_msg]
        except Exception as e:
            error_msg = f"Error extracting practice location data: {str(e)}"
            # log.error(f"DataExtractionService: {error_msg}")
            return None, [error_msg]

    def extract_all_data_for_pdmp(self, patient_id: str, practitioner_id: Optional[str]) -> Tuple[
        Optional[dict], List[str]]:
        """Extract all required data from Canvas for PDMP request."""
        all_errors = []

        try:
            # Extract patient data
            # log.info(f"PDMP-DataExtractor: Starting patient data extraction for ID: {patient_id}")
            patient_dto, patient_errors = self.extract_patient(patient_id)
            all_errors.extend(patient_errors)
            # log.info(
            #     f"PDMP-DataExtractor: Patient data extraction completed. Success: {bool(patient_dto)}, Errors: {len(patient_errors)}")

            # Extract practitioner data
            # log.info(f"PDMP-DataExtractor: Starting practitioner data extraction for ID: {practitioner_id}")
            practitioner_dto, practitioner_errors = self.extract_practitioner(practitioner_id)
            all_errors.extend(practitioner_errors)
            # log.info(
            #     f"PDMP-DataExtractor: Practitioner data extraction completed. Success: {bool(practitioner_dto)}, Errors: {len(practitioner_errors)}")

            # Extract organization data
            organization_dto = None
            organization_errors = []

            if practitioner_dto and practitioner_dto.organization_id:
                # log.info(f"PDMP-DataExtractor: Using practitioner's organization: {practitioner_dto.organization_id}")
                organization_dto, organization_errors = self.extract_organization(practitioner_dto.organization_id)
                all_errors.extend(organization_errors)
                # log.info(
                #     f"PDMP-DataExtractor: Organization data extraction completed. Success: {bool(organization_dto)}, Errors: {len(organization_errors)}")
            else:
                # log.error("PDMP-DataExtractor: No organization ID from practitioner")
                organization_errors.append("No organization ID from practitioner")
                all_errors.extend(organization_errors)

            # Extract practice location data
            practice_location_dto = None
            practice_location_errors = []

            if practitioner_dto and practitioner_dto.practice_location_id:
                # log.info(
                #     f"PDMP-DataExtractor: Using practitioner's practice location: {practitioner_dto.practice_location_id}")
                practice_location_dto, practice_location_errors = self.extract_practice_location(
                    practitioner_dto.practice_location_id)
                all_errors.extend(practice_location_errors)
                # log.info(
                #     f"PDMP-DataExtractor: Practice location data extraction completed. Success: {bool(practice_location_dto)}, Errors: {len(practice_location_errors)}")
            else:
                # log.error("PDMP-DataExtractor: No practice location ID from practitioner")
                practice_location_errors.append("No practice location ID from practitioner")
                all_errors.extend(practice_location_errors)

            # Combine all data
            all_data = {
                "patient": patient_dto,
                "practitioner": practitioner_dto,
                "organization": organization_dto,
                "practice_location": practice_location_dto,
                "extraction_errors": all_errors,
            }

            # log.info(f"PDMP-DataExtractor: Data extraction complete - {len(all_errors)} errors found")
            return all_data, all_errors

        except Exception as e:
            # log.error(f"PDMP-DataExtractor: Error in extract_all_data_for_pdmp: {str(e)}")
            import traceback
            # log.error(f"PDMP-DataExtractor: Traceback: {traceback.format_exc()}")
            return None, [f"Critical error in data extraction: {str(e)}"]


def extract_all_data_for_pdmp(self, patient_id: str, practitioner_id: str) -> tuple[
    Optional[Dict[str, Any]], List[str]]:
    """
    Extract all data needed for PDMP requests using the new architecture.

    This function provides backward compatibility with the old API while using the new architecture.

    Args:
        patient_id: Canvas patient ID
        practitioner_id: Canvas practitioner ID

    Returns:
        Tuple of (extracted_data_dict, errors)
    """
    # log.info(
    #     f"DataExtractionService: Extracting all data for PDMP - Patient: {patient_id}, Practitioner: {practitioner_id}")

    try:
        # Extract patient data
        patient_dto, patient_errors = self.extract_patient(patient_id)
        if not patient_dto:
            # log.error("DataExtractionService: Failed to extract patient data")
            return None, patient_errors

        # Extract practitioner data
        practitioner_dto, practitioner_errors = self.extract_practitioner(practitioner_id)
        if not practitioner_dto:
            # log.error("DataExtractionService: Failed to extract practitioner data")
            return None, practitioner_errors

        # Extract organization data
        organization_dto, organization_errors = self.extract_organization(practitioner_dto.organization_id)
        if not organization_dto:
            # log.error("DataExtractionService: Failed to extract organization data")
            return None, organization_errors

        # Extract practice location data
        practice_location_dto, practice_location_errors = self.extract_practice_location(
            practitioner_dto.practice_location_id)
        if not practice_location_dto:
            # log.error("DataExtractionService: Failed to extract practice location data")
            return None, practice_location_errors

        # Convert DTOs to dictionary format for backward compatibility
        extracted_data = {
            "patient": self._dto_to_dict(patient_dto),
            "practitioner": self._dto_to_dict(practitioner_dto),
            "organization": self._dto_to_dict(organization_dto),
            "practice_location": self._dto_to_dict(practice_location_dto)
        }

        # Collect all errors
        all_errors = patient_errors + practitioner_errors + organization_errors + practice_location_errors

        # log.info(f"DataExtractionService: All data extracted successfully. Errors: {len(all_errors)}")
        return extracted_data, all_errors

    except Exception as e:
        error_msg = f"Error extracting all data for PDMP: {str(e)}"
        # log.error(f"DataExtractionService: {error_msg}")
        return None, [error_msg]


def _dto_to_dict(self, dto) -> Dict[str, Any]:
    """Convert a DTO object to dictionary format."""
    if not dto:
        return {}

    # Convert DTO to dictionary by getting all attributes
    result = {}
    for attr_name in dir(dto):
        if not attr_name.startswith('_') and not callable(getattr(dto, attr_name)):
            result[attr_name] = getattr(dto, attr_name)

    return result