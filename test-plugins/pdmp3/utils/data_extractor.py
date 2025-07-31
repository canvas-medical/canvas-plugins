"""
Data Extraction from Canvas Models
"""

from typing import Dict, Any, Optional
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.organization import Organization
from canvas_sdk.v1.data.practicelocation import PracticeLocation
from logger import log


class PDMPDataExtractor:
    """Extracts and formats data from Canvas SDK models."""

    @staticmethod
    def get_patient_data(patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetches and formats patient data from the Canvas database."""
        try:
            patient = Patient.objects.get(id=patient_id)
            address = (
                patient.addresses.first()
                if hasattr(patient, "addresses") and patient.addresses.all()
                else None
            )

            # Normalize sex code to PDMP standards
            sex_code = patient.sex_at_birth or ""
            if sex_code.upper() in ["UNK", "UNKNOWN", "U"]:
                sex_code = "U"  # Use 'U' for unknown instead of 'UNK'
            elif sex_code.upper() in ["MALE", "M"]:
                sex_code = "M"
            elif sex_code.upper() in ["FEMALE", "F"]:
                sex_code = "F"
            else:
                sex_code = "U"  # Default to unknown for any other values
                log.info(f"PDMP3: Normalized unknown sex code '{patient.sex_at_birth}' to 'U'")

            return {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "dob": patient.birth_date.strftime("%Y-%m-%d") if patient.birth_date else "",
                "sex": sex_code,
                "address": {
                    "street": address.line1 if address else "",
                    "city": address.city if address else "",
                    "state": address.state_code if address else "",
                    "zip_code": address.postal_code if address else "",
                },
            }
        except Patient.DoesNotExist:
            log.warning(f"Patient with ID '{patient_id}' not found.")
            return None

    @staticmethod
    def get_staff_data(staff_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Fetches and formats staff data from the Canvas database."""
        if not staff_id:
            return None
        try:
            staff = Staff.objects.get(id=staff_id)

            # Only include valid identifiers, not "N/A" placeholders
            npi_number = staff.npi_number if staff.npi_number else ""
            dea_number = (
                getattr(staff, "nadean_number", None) or getattr(staff, "dea_number", None) or ""
            )

            return {
                "full_name": f"{staff.first_name} {staff.last_name}",
                "first_name": staff.first_name,
                "last_name": staff.last_name,
                "npi": npi_number,
                "dea_number": dea_number,
                "role": "Physician",
            }
        except Staff.DoesNotExist:
            log.warning(f"Staff with ID '{staff_id}' not found.")
            return None

    @staticmethod
    def get_facility_data(
        patient_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches and formats facility data from Canvas organization and practice location.

        Args:
            patient_data: Optional patient data to extract state information as fallback
        """
        try:
            # Try to get the main organization first
            organization = Organization.objects.filter(active=True).first()
            if not organization:
                log.warning("PDMP3: No active organization found.")
                return None

            # Get the main location from the organization
            practice_location = (
                organization.main_location if hasattr(organization, "main_location") else None
            )

            # If no main location, try to get the first active practice location
            if not practice_location:
                practice_location = PracticeLocation.objects.filter(active=True).first()

            if not practice_location:
                log.warning("PDMP3: No active practice location found.")
                return None

            log.info(f"PDMP3: Found practice location: {practice_location.full_name}")

            # Extract facility data
            facility_data = {
                "name": practice_location.full_name or "",
                "npi": practice_location.npi_number or "",
                "dea": "",  # DEA number might need to come from organization or practice settings
                "state": "",  # Will be determined below
                "street": "",  # Address information not directly available in PracticeLocation model
                "city": "",
                "zip_code": "",
            }

            # Try to get additional info from organization if available
            if organization:
                # Use group NPI if practice location NPI is not available
                if not facility_data["npi"] and organization.group_npi_number:
                    facility_data["npi"] = organization.group_npi_number
                    log.info(
                        f"PDMP3: Using organization group NPI: {organization.group_npi_number}"
                    )

            # Try to infer state from patient data if facility state is not available
            # This is a reasonable fallback since the facility is likely in the same state as the patient
            if (
                not facility_data["state"]
                and patient_data
                and patient_data.get("address", {}).get("state")
            ):
                facility_data["state"] = patient_data["address"]["state"]
                log.info(f"PDMP3: Using patient state as facility state: {facility_data['state']}")

            # Log what we found and what's missing
            log.info(
                f"PDMP3: Extracted facility data - Name: '{facility_data['name']}', NPI: '{facility_data['npi']}', State: '{facility_data['state']}'"
            )

            missing_fields = []
            if not facility_data["name"]:
                missing_fields.append("name")
            if not facility_data["npi"]:
                missing_fields.append("NPI")
            if not facility_data["state"]:
                missing_fields.append("state")

            if missing_fields:
                log.warning(f"PDMP3: Facility data missing fields: {', '.join(missing_fields)}")

            return facility_data

        except Exception as e:
            log.error(f"PDMP3: Error extracting facility data: {e}")
            return None
