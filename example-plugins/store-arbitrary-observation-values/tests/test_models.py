# To run the tests, use the command `pytest` in the terminal or uv run pytest.
# Each test is wrapped inside a transaction that is rolled back at the end of the test.
# If you want to modify which files are used for testing, check the [tool.pytest.ini_options] section in pyproject.toml.
# For more information on testing Canvas plugins, see: https://docs.canvasmedical.com/sdk/testing-utils/

import json
from unittest.mock import Mock

from store_arbitrary_observation_values.protocols.my_protocol import Protocol

from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType


def test_protocol_responds_to_glucose_observation() -> None:
    """Test that the protocol responds correctly to glucose OBSERVATION_CREATED events."""
    # Create a mock glucose observation event with context and target
    mock_event = Mock()
    mock_event.type = EventType.OBSERVATION_CREATED
    mock_event.context = {
        "observation": {
            "id": "obs-123",
            "patient_id": "patient-456",
            "code": {
                "system": "http://loinc.org",
                "code": "2345-7",  # Glucose [Mass/volume] in Serum or Plasma
                "display": "Glucose [Mass/volume] in Serum or Plasma",
            },
        }
    }
    mock_event.target = {"id": "obs-123", "value": "95", "unit": "mg/dL"}

    # Instantiate the protocol with the mock event
    protocol = Protocol(event=mock_event)

    # Call compute and get the effects
    effects = protocol.compute()

    # Assert that one effect was returned
    assert len(effects) == 1

    # Assert the effect has the correct type
    assert effects[0].type == EffectType.LOG

    # Parse the payload to verify its structure
    payload = json.loads(effects[0].payload)
    assert payload["event_type"] == "OBSERVATION_CREATED"
    assert payload["target"] == mock_event.target
    assert payload["context"] == mock_event.context


def test_protocol_ignores_non_glucose_observation() -> None:
    """Test that the protocol ignores non-glucose observations."""
    # Create a mock non-glucose observation event (BMI)
    mock_event = Mock()
    mock_event.type = EventType.OBSERVATION_CREATED
    mock_event.context = {
        "observation": {
            "id": "obs-789",
            "patient_id": "patient-101",
            "code": {
                "system": "http://loinc.org",
                "code": "39156-5",  # BMI - not glucose
                "display": "Body mass index (BMI) [Ratio]",
            },
        }
    }
    mock_event.target = {"id": "obs-789", "value": "24.5", "unit": "kg/m2"}

    # Instantiate the protocol
    protocol = Protocol(event=mock_event)

    # Call compute
    effects = protocol.compute()

    # Assert that no effects were returned (early return)
    assert len(effects) == 0


def test_protocol_event_configuration() -> None:
    """Test that the protocol is configured to respond to the correct event type."""
    assert EventType.Name(EventType.OBSERVATION_CREATED) == Protocol.RESPONDS_TO


def test_protocol_handles_multiple_glucose_loinc_codes() -> None:
    """Test that the protocol handles different glucose LOINC codes."""
    glucose_codes = [
        "2339-0",  # Glucose [Mass/volume] in Blood
        "41653-7",  # Glucose [Mass/volume] in Capillary blood by Glucometer
        "1558-6",  # Fasting glucose [Mass/volume] in Serum or Plasma
    ]

    for code in glucose_codes:
        # Create a mock event with a specific glucose LOINC code
        mock_event = Mock()
        mock_event.type = EventType.OBSERVATION_CREATED
        mock_event.context = {
            "observation": {
                "id": f"obs-{code}",
                "patient_id": "patient-123",
                "code": {"system": "http://loinc.org", "code": code, "display": f"Glucose code {code}"},
            }
        }
        mock_event.target = {"id": f"obs-{code}", "value": "100", "unit": "mg/dL"}

        # Instantiate the protocol
        protocol = Protocol(event=mock_event)

        # Call compute
        effects = protocol.compute()

        # Assert that an effect was returned for each glucose code
        assert len(effects) == 1
        assert effects[0].type == EffectType.LOG

        payload = json.loads(effects[0].payload)
        assert payload["context"]["observation"]["code"]["code"] == code


def test_protocol_handles_observation_without_code() -> None:
    """Test that the protocol handles observations without a code field gracefully."""
    # Create a mock event without a code
    mock_event = Mock()
    mock_event.type = EventType.OBSERVATION_CREATED
    mock_event.context = {"observation": {"id": "obs-no-code"}}
    mock_event.target = {"id": "obs-no-code"}

    # Instantiate the protocol
    protocol = Protocol(event=mock_event)

    # Call compute
    effects = protocol.compute()

    # Assert that no effects were returned (should return early)
    assert len(effects) == 0


def test_protocol_logs_glucometer_reading() -> None:
    """Test that the protocol handles glucometer readings (capillary blood glucose)."""
    # Create a mock glucometer reading event
    mock_event = Mock()
    mock_event.type = EventType.OBSERVATION_CREATED
    mock_event.context = {
        "observation": {
            "id": "obs-glucometer",
            "patient_id": "patient-999",
            "status": "final",
            "code": {
                "system": "http://loinc.org",
                "code": "41653-7",  # Glucose [Mass/volume] in Capillary blood by Glucometer
                "display": "Glucose [Mass/volume] in Capillary blood by Glucometer",
            },
        },
        "note": {"uuid": "note-uuid-xyz"},
    }
    mock_event.target = {"id": "obs-glucometer", "value": "120", "unit": "mg/dL"}

    # Instantiate the protocol
    protocol = Protocol(event=mock_event)

    # Call compute
    effects = protocol.compute()

    # Verify the effect contains all expected data
    assert len(effects) == 1
    payload = json.loads(effects[0].payload)

    # Verify target details are present
    assert payload["target"]["id"] == "obs-glucometer"
    assert payload["target"]["value"] == "120"
    assert payload["target"]["unit"] == "mg/dL"

    # Verify context details are present
    assert payload["context"]["observation"]["code"]["code"] == "41653-7"
    assert payload["context"]["note"]["uuid"] == "note-uuid-xyz"
