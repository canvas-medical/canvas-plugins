from dataclasses import dataclass


@dataclass(frozen=True)
class Secrets:
    """Secret key names for AWS S3 credentials stored in the plugin secrets."""

    s3_key: str = "S3Key"
    s3_secret: str = "S3Secret"
    s3_region: str = "S3Region"
    s3_bucket: str = "S3Bucket"
