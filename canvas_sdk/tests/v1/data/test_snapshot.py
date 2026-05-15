from unittest.mock import patch

from canvas_sdk.v1.data.coverage import Coverage
from canvas_sdk.v1.data.snapshot import Snapshot, SnapshotImage


def test_snapshot_str() -> None:
    """__str__ returns a readable representation."""
    snapshot = Snapshot()
    snapshot.dbid = 42
    snapshot.title = "Front view"

    assert str(snapshot) == "Snapshot(dbid=42, title=Front view)"


def test_snapshot_image_str() -> None:
    """__str__ returns a readable representation."""
    image = SnapshotImage()
    image.dbid = 7
    image.title = "Left side"
    image.tag = "wound"

    assert str(image) == "SnapshotImage(dbid=7, title=Left side, tag=wound)"


def test_snapshot_image_url_with_image() -> None:
    """image_url returns a presigned URL when image is set."""
    image = SnapshotImage()
    image.image = "snapshots/img.jpg"

    with patch(
        "canvas_sdk.v1.data.snapshot.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert image.image_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("snapshots/img.jpg")


def test_snapshot_image_url_without_image() -> None:
    """image_url returns None when image is empty."""
    image = SnapshotImage()
    image.image = ""

    assert image.image_url is None


def test_coverage_has_snapshot_fk() -> None:
    """Coverage.snapshot FK allows navigating to the linked Snapshot."""
    snapshot = Snapshot()
    snapshot.title = "Insurance card"

    coverage = Coverage()
    coverage.snapshot = snapshot

    assert coverage.snapshot is snapshot
    assert coverage.snapshot.title == "Insurance card"


def test_coverage_snapshot_is_nullable() -> None:
    """Coverage.snapshot can be None when no card images exist."""
    coverage = Coverage()

    assert coverage.snapshot is None
