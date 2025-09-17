"""
XML Generation Package for PDMP Requests

This package provides a clean, modular architecture for generating PDMP XML requests.
It separates concerns into builders, validators, and utilities for better maintainability.

Architecture:
- builders/: Specialized builders for different XML sections
- utils/: Utilities for data conversion and XML manipulation
"""

# Import builders
from pdmp_bamboo.xml.builders import (
    BaseXMLBuilder,
    PatientXMLBuilder,
    PractitionerXMLBuilder,
    LocationXMLBuilder,
    RequestXMLBuilder,
    ReportRequestXMLBuilder,
)

# Import utilities
from pdmp_bamboo.xml.utils import (
    DTOToXMLConverter,
    XMLUtils
)

# Main service for XML generation
from pdmp_bamboo.services.xml_generation import XMLGenerationService

__all__ = [
    # Builders
    'BaseXMLBuilder',
    'PatientXMLBuilder',
    'PractitionerXMLBuilder',
    'LocationXMLBuilder',
    'RequestXMLBuilder',
    'ReportRequestXMLBuilder',


    # Utilities
    'DTOToXMLConverter',
    'XMLUtils',

    # Services
    'XMLGenerationService'
]