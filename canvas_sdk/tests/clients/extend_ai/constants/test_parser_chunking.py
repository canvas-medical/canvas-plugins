from canvas_sdk.clients.extend_ai.constants.parser_chunking import ParserChunking


def test_enum() -> None:
    """Test that ParserChunking enum has all expected values for chunking strategies."""
    tested = ParserChunking
    assert len(tested) == 3
    assert tested.PAGE.value == "page"
    assert tested.DOCUMENT.value == "document"
    assert tested.SECTION.value == "section"
