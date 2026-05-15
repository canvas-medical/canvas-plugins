from canvas_sdk.clients.extend_ai.constants.parser_target import ParserTarget


def test_enum() -> None:
    """Test that ParserTarget enum has all expected values for parser output formats."""
    tested = ParserTarget
    assert len(tested) == 2
    assert tested.MARKDOWN.value == "markdown"
    assert tested.SPATIAL.value == "spatial"
