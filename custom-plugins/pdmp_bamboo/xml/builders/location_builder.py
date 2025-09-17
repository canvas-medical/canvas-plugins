"""
Location XML Builder

Builds the Location section of PDMP XML requests.
"""

from typing import Dict, Any
from pdmp_bamboo.xml.builders.base_builder import BaseXMLBuilder
from logger import log


class LocationXMLBuilder(BaseXMLBuilder):
    """Builds Location XML section for PDMP requests."""

    def build(self, data: Dict[str, Any]) -> str:
        """Build Location XML section from organization and practice location data."""
        self._log_building("Location", data)

        practice_location_data = data.get('practice_location', {})

        if not practice_location_data:
            log.warning("LocationXMLBuilder: No practice location data available")

        # Extract location info
        name = practice_location_data.get('name', '')
        npi = practice_location_data.get('npi', '')
        address_data = practice_location_data.get('address', {})

        # Build address section with correct structure
        address_xml = self._build_address_section(address_data)

        # Build Location section (no wrapper needed - RequestXMLBuilder handles it)
        location_xml = f"""<Location>
          <Name>{self._escape_xml(name)}</Name>
          <NPINumber>{self._escape_xml(npi)}</NPINumber>
          {address_xml}
        </Location>"""

        log.info("LocationXMLBuilder: Location section built successfully")
        return location_xml

    def _build_address_section(self, address_data: Dict[str, Any]) -> str:
        """Build address section with correct Street elements."""
        if not address_data:
            return ""

        street = address_data.get('street', '')
        street2 = address_data.get('street2', '')
        city = address_data.get('city', '')
        state = address_data.get('state', 'KS')  # Default to KS for PREP
        zip_code = address_data.get('zip_code', '')

        # Build Street elements (use multiple Street, not Street2)
        street_elements = []
        if street:
            street_elements.append(f"<Street>{self._escape_xml(street)}</Street>")
        if street2:
            street_elements.append(f"<Street>{self._escape_xml(street2)}</Street>")

        street_xml = '\n        '.join(street_elements)

        return f"""<Address>
            {street_xml}
            <City>{self._escape_xml(city)}</City>
            <StateCode>{self._escape_xml(state)}</StateCode>
            <ZipCode>{self._escape_xml(zip_code)}</ZipCode>
          </Address>"""

    def _get_location_name(self, organization_data: Dict[str, Any], practice_location_data: Dict[str, Any]) -> str:
        """Get the best location name from available data."""
        if practice_location_data and practice_location_data.get('name'):
            return practice_location_data['name']

        if organization_data and organization_data.get('name'):
            return organization_data['name']

        return "Unknown Location"

    def _get_npi_number(self, organization_data: Dict[str, Any], practice_location_data: Dict[str, Any]) -> str:
        """Get NPI number, preferring practice location over organization."""
        if practice_location_data and practice_location_data.get('npi'):
            return practice_location_data['npi']

        if organization_data and organization_data.get('group_npi'):
            return organization_data['group_npi']

        return ""
