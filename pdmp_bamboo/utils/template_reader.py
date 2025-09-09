"""
Template Reader Utility for PDMP Bamboo Plugin

This module provides functionality to read XML template files for mock PDMP requests.
"""

from typing import Optional
from logger import log


def read_template_xml(template_name: str = "patient-request.xml") -> Optional[str]:
    """
    Read XML template file from templates directory.

    Args:
        template_name: Name of the template file to read

    Returns:
        XML content as string, or None if file cannot be read
    """
    try:
        # Build template path relative to plugin root
        module_path = __file__
        base_dir = "/".join(
            module_path.split("/")[:-2]
        )  # Go up 2 levels from utils/template_reader.py
        template_path = f"{base_dir}/templates/{template_name}"

        log.info(f"PDMP-TemplateReader: Reading template from: {template_path}")

        # Read template content (file existence check handled by try-catch)
        with open(template_path, "r", encoding="utf-8") as template_file:
            xml_content = template_file.read()

        log.info(f"PDMP-TemplateReader: Successfully read template ({len(xml_content)} characters)")
        return xml_content

    except FileNotFoundError:
        log.error(f"PDMP-TemplateReader: Template file not found: {template_path}")
        return None
    except Exception as e:
        log.error(f"PDMP-TemplateReader: Error reading template file: {str(e)}")
        return None


def get_mock_patient_data() -> dict:
    """
    Get mock patient data extracted from the template for display purposes.

    Returns:
        Dictionary with mock patient information for display in modals
    """
    return {
        "patient": {
            "first_name": "Bob",
            "middle_name": "Dylan",
            "last_name": "Testpatient",
            "birth_date": "1900-01-01",
            "sex": "M",
            "phone": "1234567890",
            "ssn": "123-45-6789",
            "mrn": "XX-1234-AnyString",
            "address": {
                "street": "123 Main St",
                "street2": "Apt B",
                "city": "Wichita",
                "state": "KS",
                "zip_code": "67203",
            },
        },
        "practitioner": {
            "first_name": "Jon",
            "last_name": "Doe",
            "role": "Physician",
            "dea_number": "AB1234577-12345",
            "npi_number": "1212345671",
        },
        "organization": {
            "name": "Store #123",
            "practice_location": {
                "name": "Store #123",
                "npi": "1234567890",
                "dea": "AB1234579",
                "ncpdp": "1234567",
                "address": {
                    "street": "Street 1",
                    "street2": "Street 2",
                    "city": "City",
                    "state": "KS",
                    "zip_code": "40242",
                    "zip_plus_four": "4242",
                },
            },
        },
    }
