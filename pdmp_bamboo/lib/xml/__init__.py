"""
XML Generation Package for PDMP Requests.

This package provides a clean, modular architecture for generating PDMP XML requests.
It separates concerns into builders, validators, and utilities for better maintainability.

Architecture:
- builders/: Specialized builders for different XML sections
- utils/: Utilities for data conversion and XML manipulation
"""

# Import builders
from pdmp_bamboo.lib.xml.builders import (
    BaseXMLBuilder,
    LocationXMLBuilder,
    PatientRequestXMLBuilder,
    PatientXMLBuilder,
    PractitionerXMLBuilder,
    ReportRequestXMLBuilder,
)

# Import utilities
from pdmp_bamboo.lib.xml.utils import DTOToXMLConverter, XMLUtils

__all__ = [
    # Builders
    "BaseXMLBuilder",
    "PatientXMLBuilder",
    "PractitionerXMLBuilder",
    "LocationXMLBuilder",
    "PatientRequestXMLBuilder",
    "ReportRequestXMLBuilder",
    # Utilities
    "DTOToXMLConverter",
    "XMLUtils",
]
