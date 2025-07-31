"""
PDMP Data Validation Utilities for pdmp3
"""

from typing import Dict, Any
import re
from logger import log


class PDMPDataValidator:
    """
    Validates that all data required by the BambooHealth PMP Gateway API is
    present and correctly formatted before generating the XML payload.
    """

    @staticmethod
    def _is_valid_dea(dea: str) -> bool:
        """Validates DEA number format."""
        if not dea:
            return False
        return re.match(r"^[A-Z]{2}\d{7}(-\d+)?$", dea) is not None

    @staticmethod
    def _is_valid_npi(npi: str) -> bool:
        """Validates NPI number format."""
        if not npi:
            return False
        return re.match(r"^\d{10}$", npi) is not None

    @staticmethod
    def validate_patient_data_for_xml(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates all required patient fields based on PMP Gateway docs.
        """
        missing_fields = []
        errors = []

        required_patient = ["first_name", "last_name", "dob", "sex"]
        for field in required_patient:
            if not patient_data.get(field) or patient_data[field] == "N/A":
                missing_fields.append(f"Patient {field.replace('_', ' ')}")

        address = patient_data.get("address", {})
        required_address = ["street", "city", "state", "zip_code"]
        for field in required_address:
            if not address.get(field):
                missing_fields.append(f"Patient Address {field.replace('_', ' ')}")

        birth_date = patient_data.get("dob")
        if birth_date and birth_date != "N/A" and not re.match(r"^\d{4}-\d{2}-\d{2}$", birth_date):
            errors.append(f"Invalid patient dob format: {birth_date}")

        sex_code = patient_data.get("sex")
        if sex_code and sex_code != "N/A" and sex_code not in ["M", "F", "U"]:
            errors.append(f"Invalid patient sex code: {sex_code}")

        return {
            "is_valid": not missing_fields and not errors,
            "missing_fields": missing_fields,
            "errors": errors,
        }

    @staticmethod
    def validate_practitioner_data_for_xml(practitioner_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates all required practitioner fields. At least one identifier
        (NPI, DEA, or license) is required.
        """
        missing_fields = []
        errors = []

        required_practitioner = ["full_name", "role"]
        for field in required_practitioner:
            if not practitioner_data.get(field) or practitioner_data[field] == "N/A":
                missing_fields.append(f"Provider {field.replace('_', ' ')}")

        has_identifier = any(
            [
                practitioner_data.get("npi"),
                practitioner_data.get("dea_number"),
                practitioner_data.get("license_number"),
            ]
        )
        if not has_identifier:
            missing_fields.append("Provider DEA, NPI, or professional license number")

        npi = practitioner_data.get("npi")
        if npi and npi != "N/A" and not PDMPDataValidator._is_valid_npi(npi):
            errors.append(f"Invalid NPI format: {npi}")

        dea = practitioner_data.get("dea_number")
        if dea and dea != "N/A" and not PDMPDataValidator._is_valid_dea(dea):
            errors.append(f"Invalid DEA format: {dea}")

        return {
            "is_valid": not missing_fields and not errors,
            "missing_fields": missing_fields,
            "errors": errors,
        }

    @staticmethod
    def validate_location_data_for_xml(location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates all required facility/location fields.
        """
        missing_fields = []
        errors = []

        if not location_data.get("name"):
            missing_fields.append("Facility name")

        if not location_data.get("state"):
            missing_fields.append("Facility state")

        has_identifier = any([location_data.get("dea"), location_data.get("npi")])
        if not has_identifier:
            missing_fields.append("Facility DEA or NPI Number")

        return {
            "is_valid": not missing_fields and not errors,
            "missing_fields": missing_fields,
            "errors": errors,
        }

    @staticmethod
    def validate_xml_data_complete(
        patient_data: Dict[str, Any],
        practitioner_data: Dict[str, Any],
        location_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validates all required data for XML generation by combining patient, practitioner, and location validation.

        Args:
            patient_data: Patient information dictionary
            practitioner_data: Practitioner information dictionary
            location_data: Location/facility information dictionary

        Returns:
            Dict with 'valid' (bool) and 'missing_fields' (list) keys
        """
        all_missing_fields = []
        all_errors = []

        # Validate patient data
        patient_validation = PDMPDataValidator.validate_patient_data_for_xml(patient_data)
        all_missing_fields.extend(patient_validation["missing_fields"])
        all_errors.extend(patient_validation["errors"])

        # Validate practitioner data
        practitioner_validation = PDMPDataValidator.validate_practitioner_data_for_xml(
            practitioner_data
        )
        all_missing_fields.extend(practitioner_validation["missing_fields"])
        all_errors.extend(practitioner_validation["errors"])

        # Validate location data
        location_validation = PDMPDataValidator.validate_location_data_for_xml(location_data)
        all_missing_fields.extend(location_validation["missing_fields"])
        all_errors.extend(location_validation["errors"])

        # Return in the format expected by calling code
        return {
            "valid": not all_missing_fields and not all_errors,
            "missing_fields": all_missing_fields + [f"Error: {err}" for err in all_errors],
        }
