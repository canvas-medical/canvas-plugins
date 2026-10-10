"""
XML Utilities.

Common utilities for XML generation.
"""

from typing import Any

from logger import log


class XMLUtils:
    """Utility functions for XML generation."""

    @staticmethod
    def validate_xml_data(xml_data: dict[str, Any]) -> bool:
        """Basic validation of XML data structure."""
        required_sections = [
            "patient",
            "practitioner",
            "organization",
            "practice_location",
            "metadata",
        ]

        for section in required_sections:
            if section not in xml_data:
                log.error(f"XMLUtils: Missing required section: {section}")
                return False

        return True

    @staticmethod
    def log_xml_data(xml_data: dict[str, Any]) -> None:
        """Log XML data summary for debugging."""
        sections = [k for k in xml_data if k != "metadata"]
        log.info(f"XML data prepared: {', '.join(sections)}")
