from canvas_sdk.clients.twillio.constants.date_operation import DateOperation


def test_enum() -> None:
    """Test DateOperation enum has correct values and member count."""
    tested = DateOperation
    assert len(tested) == 3
    assert tested.ON_EXACTLY.value == "ON"
    assert tested.ON_AND_BEFORE.value == "BEFORE"
    assert tested.ON_AND_AFTER.value == "AFTER"
