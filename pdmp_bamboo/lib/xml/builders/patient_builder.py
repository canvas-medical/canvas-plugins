"""
Patient XML Builder.

Builds the Patient section of PDMP XML requests.
"""

from typing import Any

from logger import log
from pdmp_bamboo.lib.xml.builders.base_builder import BaseXMLBuilder


class PatientXMLBuilder(BaseXMLBuilder):
    """Builds Patient XML section for PDMP requests."""

    def build(self, patient_data: dict[str, Any]) -> str:
        """Build Patient XML section from patient data."""
        self._log_building("Patient", patient_data)

        if not patient_data:
            log.warning(
                "PatientXMLBuilder: No patient data available, creating minimal Patient section"
            )
            return self._build_minimal_patient()

        # Build name section
        name_xml = self._build_name_section(patient_data)

        # Build basic info
        birthdate = patient_data.get("birth_date", "")
        sex_code = patient_data.get("sex", "U")

        # Build address section
        address_xml = self._build_address_section(patient_data.get("address", {}))

        # Build optional elements
        phone_xml = self._build_optional_element("Phone", patient_data.get("phone"))
        ssn_xml = self._build_optional_element("SSN", patient_data.get("ssn"))
        mrn_xml = self._build_optional_element("MedicalRecordID", patient_data.get("mrn"))

        # Build Patient section (no wrapper needed - RequestXMLBuilder handles it)
        patient_xml = f"""<Patient>
          {name_xml}
          <Birthdate>{self._escape_xml(birthdate)}</Birthdate>
          <SexCode>{self._escape_xml(sex_code)}</SexCode>
          {address_xml}
          {phone_xml}
          {ssn_xml}
          {mrn_xml}
        </Patient>"""

        log.info("PatientXMLBuilder: Patient section built successfully")
        return patient_xml

    def _build_minimal_patient(self) -> str:
        """Build minimal patient section when no data is available."""
        return """<Patient>
      <Name>
        <First></First>
        <Last></Last>
      </Name>
      <Birthdate></Birthdate>
      <SexCode>U</SexCode>
    </Patient>"""

    def _build_name_section(self, patient_data: dict[str, Any]) -> str:
        """Build the Name XML section."""
        first_name = patient_data.get("first_name", "")
        last_name = patient_data.get("last_name", "")
        middle_name = patient_data.get("middle_name")

        name_xml = f"""<Name>
        <First>{self._escape_xml(first_name)}</First>"""

        if middle_name:
            name_xml += f"\n        <Middle>{self._escape_xml(middle_name)}</Middle>"

        name_xml += f"""
        <Last>{self._escape_xml(last_name)}</Last>
      </Name>"""

        return name_xml

    def _build_address_section(self, address_data: dict[str, Any]) -> str:
        """Build address XML section if address data exists."""
        if not address_data or not any(address_data.values()):
            return ""

        log.debug(f"PatientXMLBuilder: Building address with data: {address_data}")

        address_xml = "\n      <Address>"

        # Add street addresses
        if address_data.get("street"):
            address_xml += f"\n        <Street>{self._escape_xml(address_data['street'])}</Street>"

        if address_data.get("street2"):
            address_xml += f"\n        <Street>{self._escape_xml(address_data['street2'])}</Street>"

        # Add city, state, zip
        if address_data.get("city"):
            address_xml += f"\n        <City>{self._escape_xml(address_data['city'])}</City>"

        if address_data.get("state"):
            address_xml += f"\n        <StateCode>{self._escape_xml(address_data['state'].upper())}</StateCode>"

        if address_data.get("zip_code"):
            address_xml += (
                f"\n        <ZipCode>{self._escape_xml(address_data['zip_code'])}</ZipCode>"
            )

        address_xml += "\n      </Address>"

        return address_xml
