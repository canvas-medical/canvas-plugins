from canvas_sdk.clients.twilio.constants.http_method import HttpMethod


def test_enum() -> None:
    """Test HttpMethod enum has correct values and member count."""
    tested = HttpMethod
    assert len(tested) == 2
    assert tested.GET.value == "GET"
    assert tested.POST.value == "POST"
