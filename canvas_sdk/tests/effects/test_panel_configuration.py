import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.panel_configuration import PanelConfiguration

Page = PanelConfiguration.Page
PatientSection = PanelConfiguration.PanelPatientSection


def test_patient_sections_serialize_in_order() -> None:
    """Patient sections, including Protocols, serialize in the order given."""
    config = PanelConfiguration(
        sections=[PatientSection.TASK, PatientSection.PROTOCOL, PatientSection.LAB_REPORT],
        page=Page.PATIENT,
    )

    payload = json.loads(config.apply().payload)

    assert payload == {"data": {"sections": ["task", "protocol", "labReport"]}}


def test_protocol_is_rejected_on_the_global_page() -> None:
    """Protocols is a patient-chart button, so the global page must not accept it."""
    config = PanelConfiguration(sections=[PatientSection.PROTOCOL], page=Page.GLOBAL)

    with pytest.raises(ValidationError, match="PanelGlobalSection"):
        config.apply()
