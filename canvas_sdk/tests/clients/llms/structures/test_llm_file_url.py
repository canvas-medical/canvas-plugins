from canvas_sdk.clients.llms.constants.file_type import FileType
from canvas_sdk.clients.llms.structures.llm_file_url import LlmFileUrl


def test_named_tuple() -> None:
    """Test LlmFileUrl is a NamedTuple with exactly two fields."""
    tested = LlmFileUrl(
        url="theUrl",
        type=FileType.PDF,
    )

    assert isinstance(tested, tuple)
    assert tested[0] == "theUrl"
    assert tested[1] == FileType.PDF
    assert len(tested) == 2
