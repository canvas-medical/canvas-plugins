from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor


def test_enum() -> None:
    """Test that BaseProcessor enum has all expected values for different processor types."""
    tested = BaseProcessor
    assert len(tested) == 6
    assert tested.CLASSIFICATION_PERFORMANCE.value == "classification_performance"
    assert tested.CLASSIFICATION_LIGHT.value == "classification_light"
    assert tested.EXTRACTION_PERFORMANCE.value == "extraction_performance"
    assert tested.EXTRACTION_LIGHT.value == "extraction_light"
    assert tested.SPLITTING_PERFORMANCE.value == "splitting_performance"
    assert tested.SPLITTING_LIGHT.value == "splitting_light"
