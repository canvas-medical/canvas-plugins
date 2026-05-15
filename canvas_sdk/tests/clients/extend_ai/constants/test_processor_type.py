from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType


def test_enum() -> None:
    """Test that ProcessorType enum has all expected values for processor types."""
    tested = ProcessorType
    assert len(tested) == 3
    assert tested.EXTRACT.value == "EXTRACT"
    assert tested.CLASSIFY.value == "CLASSIFY"
    assert tested.SPLITTER.value == "SPLITTER"
