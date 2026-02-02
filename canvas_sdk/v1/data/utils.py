import datetime
import hashlib
import hmac
import random
import string
import urllib.parse
import uuid
from collections.abc import Sequence
from decimal import Decimal

from django.conf import settings


def presigned_url(
    s3_key: str,
    bucket: str | None = None,
    region: str | None = None,
    expires_in: int = 3600,
) -> str:
    """
    Generate a presigned URL for an S3 object.

    Args:
        s3_key: The S3 object key (path within the bucket).
        bucket: The S3 bucket name. Defaults to settings.MEDIA_S3_BUCKET_NAME.
        region: The AWS region. Defaults to settings.AWS_REGION.
        expires_in: URL expiration time in seconds. Defaults to 3600 (1 hour).

    Returns:
        A presigned URL string that can be used to access the S3 object.
    """
    access_key_id = settings.AWS_ACCESS_KEY_ID
    secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    bucket = bucket or settings.MEDIA_S3_BUCKET_NAME
    region = region or settings.AWS_REGION

    if not access_key_id or not secret_access_key:
        raise ValueError("AWS credentials not configured")

    # Clean the key - remove bucket prefix if present
    s3_key = s3_key.replace(f"{bucket}/", "")

    service = "s3"
    host = f"{bucket}.s3.{region}.amazonaws.com"
    endpoint = f"https://{host}"

    now = datetime.datetime.now(datetime.UTC)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")

    credential_scope = f"{datestamp}/{region}/{service}/aws4_request"
    credential = f"{access_key_id}/{credential_scope}"

    # Build canonical query string (order matters for signing)
    query_params = {
        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        "X-Amz-Credential": credential,
        "X-Amz-Date": amzdate,
        "X-Amz-Expires": str(expires_in),
        "X-Amz-SignedHeaders": "host",
    }

    # Sort and encode query parameters
    sorted_params = sorted(query_params.items())
    canonical_querystring = "&".join(
        f"{urllib.parse.quote(k, safe='~')}={urllib.parse.quote(v, safe='~')}"
        for k, v in sorted_params
    )

    # Build canonical request
    canonical_uri = "/" + urllib.parse.quote(s3_key, safe="/~")
    canonical_headers = f"host:{host}\n"
    signed_headers = "host"
    payload_hash = "UNSIGNED-PAYLOAD"

    canonical_request = (
        f"GET\n{canonical_uri}\n{canonical_querystring}\n"
        f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
    )

    # Create string to sign
    algorithm = "AWS4-HMAC-SHA256"
    string_to_sign = (
        f"{algorithm}\n{amzdate}\n{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )

    # Calculate signature
    def sign(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    date_key = sign(("AWS4" + secret_access_key).encode("utf-8"), datestamp)
    region_key = sign(date_key, region)
    service_key = sign(region_key, service)
    signing_key = sign(service_key, "aws4_request")
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    # Build final URL
    return f"{endpoint}{canonical_uri}?{canonical_querystring}&X-Amz-Signature={signature}"


def quantize(deci: Decimal | float | str | tuple[int, Sequence[int], int]) -> Decimal:
    """Rounds a Decimal value to two decimal places."""
    return Decimal(deci).quantize(Decimal(".01"))


def create_key() -> str:
    """Generates a unique key using UUID4."""
    return uuid.uuid4().hex


def generate_mrn(length: int = 9, max_attempts: int = 100) -> str:
    """Generates a unique Medical Record Number (MRN) of specified length."""
    from canvas_sdk.v1.data import Patient

    digits = string.digits

    for _ in range(max_attempts):
        mrn = "".join(random.choices(digits, k=length))
        if not Patient.objects.filter(mrn=mrn).exists():
            return mrn

    raise RuntimeError(f"Unable to generate a unique MRN after {max_attempts} attempts")


def empty_note_body() -> list[dict[str, str]]:
    """Generates an empty note body with 15 empty text elements."""
    return [{"type": "text", "value": ""}] * 15


__exports__ = ()
