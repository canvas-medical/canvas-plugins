"""
Practitioner XML Builder

Builds the Provider section of PDMP XML requests.
"""

from typing import Dict, Any
from pdmp_bamboo.xml.builders.base_builder import BaseXMLBuilder
from logger import log


class PractitionerXMLBuilder(BaseXMLBuilder):
    """Builds Provider XML section for PDMP requests."""

    def build(self, practitioner_data: Dict[str, Any]) -> str:
        """Build Provider XML section from practitioner data."""
        self._log_building("Provider", practitioner_data)

        if not practitioner_data:
            log.warning("PractitionerXMLBuilder: No practitioner data available, creating minimal Provider section")
            return self._build_minimal_provider()

        # Extract practitioner info
        role = practitioner_data.get('role', 'Physician')
        first_name = practitioner_data.get('first_name', '')
        last_name = practitioner_data.get('last_name', '')
        dea_number = practitioner_data.get('dea_number', '')
        npi_number = practitioner_data.get('npi_number', '')

        # Build Provider section (no wrapper needed - RequestXMLBuilder handles it)
        provider_xml = f"""<Provider>
          <Role>{self._escape_xml(role)}</Role>
          <FirstName>{self._escape_xml(first_name)}</FirstName>
          <LastName>{self._escape_xml(last_name)}</LastName>
          <DEANumber>{self._escape_xml(dea_number)}</DEANumber>
          <NPINumber>{self._escape_xml(npi_number)}</NPINumber>
        </Provider>"""

        log.info("PractitionerXMLBuilder: Provider section built successfully")
        return provider_xml
    
    def _build_minimal_provider(self) -> str:
        """Build minimal provider section when no data is available."""
        return """<Provider>
      <Role>Physician</Role>
      <FirstName></FirstName>
      <LastName></LastName>
    </Provider>"""
    
    def _build_license_section(self, practitioner_data: Dict[str, Any]) -> str:
        """Build professional license section."""
        license_number = practitioner_data.get('license_number')
        license_type = practitioner_data.get('license_type', 'Medical')
        license_state = practitioner_data.get('license_state')
        
        if not license_number or not license_state:
            # Fallback to NPI if no license info
            npi_number = practitioner_data.get('npi_number')
            if npi_number:
                return f"""<ProfessionalLicenseNumber>
        <Type>NPI</Type>
        <Value>{self._escape_xml(npi_number)}</Value>
        <StateCode>CA</StateCode>
      </ProfessionalLicenseNumber>"""
            return ""
        
        return f"""<ProfessionalLicenseNumber>
        <Type>{self._escape_xml(license_type)}</Type>
        <Value>{self._escape_xml(license_number)}</Value>
        <StateCode>{self._escape_xml(license_state.upper())}</StateCode>
      </ProfessionalLicenseNumber>"""
