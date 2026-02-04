from canvas_sdk.clients.llms.constants.file_type import FileType


def test_enum() -> None:
    """Test FileType is an Enum with exactly three values."""
    tested = FileType
    result = {ft.value for ft in tested}
    expected = {
        "image",
        "pdf",
        "text",
    }
    assert result == expected
