from canvas_sdk.clients.llms.structures.file_content import FileContent


def test_named_tuple() -> None:
    """Test FileContent is a NamedTuple with exactly three fields."""
    tested = FileContent(
        mime_type="text/plain",
        content=b"abcd",
        size=4,
    )

    assert isinstance(tested, tuple)
    assert tested[0] == "text/plain"
    assert tested[1] == b"abcd"
    assert tested[2] == 4
    assert len(tested) == 3
