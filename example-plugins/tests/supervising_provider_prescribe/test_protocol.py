"""Basic smoke tests for supervising_provider_prescribe plugin."""


def test_import_protocol():
    """Test that Protocol can be imported without errors."""
    from supervising_provider_prescribe.protocols.my_protocol import Protocol

    # Verify the class exists and has expected attributes
    assert Protocol is not None
    assert hasattr(Protocol, "RESPONDS_TO")
    assert hasattr(Protocol, "compute")


def test_protocol_responds_to():
    """Test that Protocol responds to PRESCRIBE_COMMAND__POST_ORIGINATE event."""
    from supervising_provider_prescribe.protocols.my_protocol import Protocol

    from canvas_sdk.events import EventType

    # Verify RESPONDS_TO is configured correctly
    assert Protocol.RESPONDS_TO == EventType.Name(EventType.PRESCRIBE_COMMAND__POST_ORIGINATE)
