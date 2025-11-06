"""Basic smoke tests for my_first_plugin."""


def test_import_protocol():
    """Test that Protocol can be imported without errors."""
    from my_first_plugin.protocols.protocol import Protocol

    # Verify the class exists and has expected attributes
    assert Protocol is not None
    assert hasattr(Protocol, "RESPONDS_TO")
    assert hasattr(Protocol, "compute")
    assert hasattr(Protocol, "NARRATIVE_STRING")


def test_protocol_configuration():
    """Test that Protocol has correct configuration."""
    from my_first_plugin.protocols.protocol import Protocol

    from canvas_sdk.events import EventType

    # Verify configuration
    assert Protocol.RESPONDS_TO == EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)
    assert Protocol.NARRATIVE_STRING == "zebra"
