from dataclasses import dataclass


@dataclass(frozen=True)
class S3:
    """S3 client constant
    - ALGORITHM: AWS signature algorithm used (AWS4-HMAC-SHA256)
    - SAFE_CHARACTERS: Characters that don't need URL encoding
    - REQUEST_TYPE: AWS request type
    - UNSIGNED_PAYLOAD: Constant for unsigned payload in presigned URLs.
    """

    SERVICE_NAME: str = "s3"
    ALGORITHM: str = "AWS4-HMAC-SHA256"
    SAFE_CHARACTERS: str = "-._~"
    REQUEST_TYPE: str = "aws4_request"
    UNSIGNED_PAYLOAD: str = "UNSIGNED-PAYLOAD"


__exports__ = ()
