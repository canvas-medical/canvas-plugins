from typing import Final


class S3:
    """S3 client constant
    - ALGORITHM: AWS signature algorithm used (AWS4-HMAC-SHA256)
    - SAFE_CHARACTERS: Characters that don't need URL encoding
    - REQUEST_TYPE: AWS request type
    - UNSIGNED_PAYLOAD: Constant for unsigned payload in presigned URLs.
    """

    SERVICE_NAME: Final = "s3"
    ALGORITHM: Final = "AWS4-HMAC-SHA256"
    SAFE_CHARACTERS: Final = "-._~"
    REQUEST_TYPE: Final = "aws4_request"
    UNSIGNED_PAYLOAD: Final = "UNSIGNED-PAYLOAD"


__exports__ = ()
