from canvas_sdk.clients.sendgrid.constants.criterion_operation import CriterionOperation


def test_enum() -> None:
    """Test CriterionOperation enum has correct values and member count."""
    tested = CriterionOperation
    assert len(tested) == 5
    assert tested.GREATER_THAN.value == ">"
    assert tested.GREATER_THAN_OR_EQUAL.value == ">="
    assert tested.LOWER_THAN.value == "<"
    assert tested.LOWER_THAN_OR_EQUAL.value == "<="
    assert tested.EQUAL.value == "="
