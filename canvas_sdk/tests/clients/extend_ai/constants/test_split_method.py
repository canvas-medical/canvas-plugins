from canvas_sdk.clients.extend_ai.constants.split_method import SplitMethod


def test_enum() -> None:
    """Test that SplitMethod enum has all expected values for document splitting methods."""
    tested = SplitMethod
    assert len(tested) == 2
    assert tested.HIGH_PRECISION.value == "high_precision"
    assert tested.LOW_LATENCY.value == "low_latency"
