from unittest.mock import patch

import pytest
from upsert_patient_metadata.protocols.my_protocol import Protocol


class DummyEvent:
    """Dummy event for Protocol instantiation in tests."""
    pass

@pytest.mark.parametrize(
    "narrative,key,value,should_upsert",
    [
        ("key=allergies*value=peanuts", "allergies", "peanuts", True),
        ("key=foo*value=bar", "foo", "bar", True),
        ("no key or value here", None, None, False),
        ("key=onlykey", None, None, False),
        ("value=onlyvalue", None, None, False),
    ],
)
def test_protocol_compute(monkeypatch, narrative, key, value, should_upsert):
    """Test Protocol.compute for various narrative patterns and upsert behavior."""
    dummy_patient_id = 123
    dummy_context = {
        "patient": {"id": dummy_patient_id},
        "fields": {"narrative": narrative},
    }
    dummy_event = DummyEvent()
    protocol = Protocol(event=dummy_event)
    monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

    # Patch PatientMetadata and its upsert method
    with patch("upsert_patient_metadata.protocols.my_protocol.PatientMetadata") as MockPatientMetadata:
        mock_instance = MockPatientMetadata.return_value
        mock_upsert = mock_instance.upsert
        mock_upsert.return_value = "upserted-effect"
        effects = protocol.compute()
        if should_upsert:
            MockPatientMetadata.assert_called_once_with(patient_id=dummy_patient_id, key=key)
            mock_upsert.assert_called_once_with(value)
            assert effects == ["upserted-effect"]
        else:
            MockPatientMetadata.assert_not_called()
            assert effects == []
