"""Basic smoke tests for supervising_provider_prescribe_protocol plugin."""


def test_import_protocol():
    """Test that Protocol can be imported without errors."""
    from supervising_provider_prescribe_protocol.protocols.my_protocol import Protocol

    # Verify the class exists and has expected attributes
    assert Protocol is not None
    assert hasattr(Protocol, "RESPONDS_TO")
    assert hasattr(Protocol, "compute")


def test_protocol_responds_to():
    """Test that Protocol has RESPONDS_TO configured."""
    from supervising_provider_prescribe_protocol.protocols.my_protocol import Protocol

    # Verify RESPONDS_TO is configured (not None)
    assert Protocol.RESPONDS_TO is not None
    assert isinstance(Protocol.RESPONDS_TO, str)
