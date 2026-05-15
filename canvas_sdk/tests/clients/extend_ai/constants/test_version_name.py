from canvas_sdk.clients.extend_ai.constants.version_name import VersionName


def test_enum() -> None:
    """Test that VersionName enum has all expected values for processor versions."""
    tested = VersionName
    assert len(tested) == 2
    assert tested.LATEST.value == "latest"
    assert tested.DRAFT.value == "draft"
