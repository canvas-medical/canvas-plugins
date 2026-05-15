from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.twilio.structures.media import Media
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Media dataclass has correct field types."""
    tested = Media
    fields = {
        "sid": str,
        "content_type": str,
        "date_created": datetime,
        "date_updated": datetime,
        "parent_sid": str,
        "uri": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "sid": "ME123",
                "content_type": "image/jpeg",
                "date_created": "Mon, 15 Dec 2025 10:30:11 +0000",
                "date_updated": "Mon, 15 Dec 2025 10:30:15 +0000",
                "parent_sid": "MM456",
                "uri": "/2010-04-01/Accounts/AC789/Messages/MM456/Media/ME123",
            },
            Media(
                sid="ME123",
                content_type="image/jpeg",
                date_created=datetime(2025, 12, 15, 10, 30, 11, tzinfo=UTC),
                date_updated=datetime(2025, 12, 15, 10, 30, 15, tzinfo=UTC),
                parent_sid="MM456",
                uri="/2010-04-01/Accounts/AC789/Messages/MM456/Media/ME123",
            ),
            id="jpeg_image",
        ),
        pytest.param(
            {
                "sid": "ME789",
                "content_type": "video/mp4",
                "date_created": "Tue, 16 Dec 2025 14:20:33 +0000",
                "date_updated": "Tue, 16 Dec 2025 14:20:35 +0000",
                "parent_sid": "MM999",
                "uri": "/2010-04-01/Accounts/AC111/Messages/MM999/Media/ME789",
            },
            Media(
                sid="ME789",
                content_type="video/mp4",
                date_created=datetime(2025, 12, 16, 14, 20, 33, tzinfo=UTC),
                date_updated=datetime(2025, 12, 16, 14, 20, 35, tzinfo=UTC),
                parent_sid="MM999",
                uri="/2010-04-01/Accounts/AC111/Messages/MM999/Media/ME789",
            ),
            id="mp4_video",
        ),
    ],
)
def test_from_dict(data: dict, expected: Media) -> None:
    """Test Media.from_dict creates instance from dictionary with datetime parsing."""
    test = Media
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("media", "expected"),
    [
        pytest.param(
            Media(
                sid="ME123",
                content_type="image/jpeg",
                date_created=datetime(2025, 12, 15, 10, 30, 11, tzinfo=UTC),
                date_updated=datetime(2025, 12, 15, 10, 30, 15, tzinfo=UTC),
                parent_sid="MM456",
                uri="/2010-04-01/Accounts/AC789/Messages/MM456/Media/ME123",
            ),
            {
                "sid": "ME123",
                "content_type": "image/jpeg",
                "date_created": "Mon, 15 Dec 2025 10:30:11 +0000",
                "date_updated": "Mon, 15 Dec 2025 10:30:15 +0000",
                "created": "2025-12-15T10:30:11+0000",
                "updated": "2025-12-15T10:30:15+0000",
                "parent_sid": "MM456",
                "uri": "/2010-04-01/Accounts/AC789/Messages/MM456/Media/ME123",
            },
            id="jpeg_image",
        ),
        pytest.param(
            Media(
                sid="ME789",
                content_type="video/mp4",
                date_created=datetime(2025, 12, 16, 14, 20, 33, tzinfo=UTC),
                date_updated=datetime(2025, 12, 16, 14, 20, 35, tzinfo=UTC),
                parent_sid="MM999",
                uri="/2010-04-01/Accounts/AC111/Messages/MM999/Media/ME789",
            ),
            {
                "sid": "ME789",
                "content_type": "video/mp4",
                "date_created": "Tue, 16 Dec 2025 14:20:33 +0000",
                "date_updated": "Tue, 16 Dec 2025 14:20:35 +0000",
                "created": "2025-12-16T14:20:33+0000",
                "updated": "2025-12-16T14:20:35+0000",
                "parent_sid": "MM999",
                "uri": "/2010-04-01/Accounts/AC111/Messages/MM999/Media/ME789",
            },
            id="mp4_video",
        ),
    ],
)
def test_to_dict(media: Media, expected: dict) -> None:
    """Test Media.to_dict converts instance to dictionary with formatted dates."""
    result = media.to_dict()
    assert result == expected
