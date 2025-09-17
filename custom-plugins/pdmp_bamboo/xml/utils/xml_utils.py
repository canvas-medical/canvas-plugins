"""
XML Utilities

Common utilities for XML generation.
"""

from typing import Dict, Any
from logger import log


class XMLUtils:
    """Utility functions for XML generation."""
    
    @staticmethod
    def validate_xml_data(xml_data: Dict[str, Any]) -> bool:
        """Basic validation of XML data structure."""
        required_sections = ['patient', 'practitioner', 'organization', 'practice_location', 'metadata']
        
        for section in required_sections:
            if section not in xml_data:
                log.error(f"XMLUtils: Missing required section: {section}")
                return False
        
        return True
    
    @staticmethod
    def log_xml_data(xml_data: Dict[str, Any]) -> None:
        """Log XML data for debugging."""
        log.info("=" * 80)
        log.info("XMLUtils: XML DATA DEBUG")
        log.info("=" * 80)
        
        for section_name, section_data in xml_data.items():
            if section_name == 'metadata':
                continue
                
            log.info(f"{section_name.upper()} DATA:")
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if key == 'address' and isinstance(value, dict):
                        log.info(f"  {key}:")
                        for addr_key, addr_value in value.items():
                            log.info(f"    {addr_key}: '{addr_value}'")
                    else:
                        log.info(f"  {key}: '{value}'")
            else:
                log.info(f"  Raw: {section_data}")
        
        log.info("=" * 80)
