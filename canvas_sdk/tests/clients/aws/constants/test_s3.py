from canvas_sdk.clients.aws.constants.s3 import S3
from canvas_sdk.tests.conftest import has_constants


def test_class() -> None:
    """Test S3Item is a frozen Dataclass with correct values."""
    assert has_constants(
        S3,
        {
            "SERVICE_NAME": "s3",
            "ALGORITHM": "AWS4-HMAC-SHA256",
            "SAFE_CHARACTERS": "-._~",
            "REQUEST_TYPE": "aws4_request",
            "UNSIGNED_PAYLOAD": "UNSIGNED-PAYLOAD",
        },
    )
