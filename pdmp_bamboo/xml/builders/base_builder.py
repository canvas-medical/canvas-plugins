"""
Base XML Builder

Abstract base class for all XML builders with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from logger import log

# class BaseXMLBuilder:
class BaseXMLBuilder(ABC):
    """Abstract base class for XML builders."""
    
    @abstractmethod
    def build(self, data: Dict[str, Any]) -> str:
        """Build XML section from data."""
        pass

    def _escape_xml(self, value: str) -> str:
        """Escape XML special characters."""
        if not value:
            return ""

        return (str(value)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

    def _build_optional_element(self, tag: str, value: Any, attributes: Optional[Dict[str, str]] = None) -> str:
        """Build optional XML element if value exists."""
        if not value:
            return ""

        attr_str = ""
        if attributes:
            attr_str = " " + " ".join([f'{k}="{self._escape_xml(v)}"' for k, v in attributes.items()])

        escaped_value = self._escape_xml(str(value))
        return f"<{tag}{attr_str}>{escaped_value}</{tag}>"

    def _build_required_element(self, tag: str, value: Any, default: str = "", attributes: Optional[Dict[str, str]] = None) -> str:
        """Build required XML element with fallback to default value."""
        actual_value = value if value is not None else default

        attr_str = ""
        if attributes:
            attr_str = " " + " ".join([f'{k}="{self._escape_xml(v)}"' for k, v in attributes.items()])

        escaped_value = self._escape_xml(str(actual_value))
        return f"<{tag}{attr_str}>{escaped_value}</{tag}>"

    def _log_building(self, section_name: str, data: Dict[str, Any]) -> None:
        """Log the building process for debugging."""
        log.info(f"XMLBuilder: Building {section_name} section")
        log.debug(f"XMLBuilder: {section_name} data: {data}")
