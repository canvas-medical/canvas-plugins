from canvas_sdk.clients.aws.constants.s3 import S3
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test S3Item is a frozen Dataclass with correct values."""
    assert is_dataclass(
        S3,
        {
            "SERVICE_NAME": str,
            "ALGORITHM": str,
            "SAFE_CHARACTERS": str,
            "REQUEST_TYPE": str,
            "UNSIGNED_PAYLOAD": str,
        },
    )
    assert S3.SERVICE_NAME == "s3"
    assert S3.ALGORITHM == "AWS4-HMAC-SHA256"
    assert S3.SAFE_CHARACTERS == "-._~"
    assert S3.REQUEST_TYPE == "aws4_request"
    assert S3.UNSIGNED_PAYLOAD == "UNSIGNED-PAYLOAD"
