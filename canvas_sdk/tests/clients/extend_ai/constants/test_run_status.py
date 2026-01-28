from canvas_sdk.clients.extend_ai.constants.run_status import RunStatus


def test_enum() -> None:
    """Test that RunStatus enum has all expected values for processor run statuses."""
    tested = RunStatus
    assert len(tested) == 5
    assert tested.PENDING.value == "PENDING"
    assert tested.PROCESSING.value == "PROCESSING"
    assert tested.PROCESSED.value == "PROCESSED"
    assert tested.FAILED.value == "FAILED"
    assert tested.CANCELLED.value == "CANCELLED"
