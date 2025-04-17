# Shamelessly cribbed from https://charemza.name/blog/posts/aws/python/you-might-not-need-boto-3/

import datetime
import hashlib
import hmac
import urllib.parse


def aws_sig_v4_headers(
    access_key_id: str,
    secret_access_key: str,
    pre_auth_headers: dict[str, str],
    service: str,
    region: str,
    host: str,
    method: str,
    path: str,
    query: dict[str, str],
    payload: bytes,
) -> dict[str, str]:
    """Constructs signed headers for use in requests made to AWS."""
    algorithm = "AWS4-HMAC-SHA256"
    now = datetime.datetime.now(datetime.UTC)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(payload).hexdigest()
    credential_scope = f"{datestamp}/{region}/{service}/aws4_request"

    pre_auth_headers_lower = {
        header_key.lower(): " ".join(header_value.split())
        for header_key, header_value in pre_auth_headers.items()
    }
    required_headers = {
        "host": host,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amzdate,
    }
    headers = {**pre_auth_headers_lower, **required_headers}
    header_keys = sorted(headers.keys())
    signed_headers = ";".join(header_keys)

    def signature() -> str:
        def canonical_request() -> str:
            canonical_uri = urllib.parse.quote(path, safe="/~")
            quoted_query = sorted(
                (urllib.parse.quote(key, safe="~"), urllib.parse.quote(value, safe="~"))
                for key, value in query.items()
            )
            canonical_querystring = "&".join(f"{key}={value}" for key, value in quoted_query)
            canonical_headers = "".join(f"{key}:{headers[key]}\n" for key in header_keys)

            return (
                f"{method}\n{canonical_uri}\n{canonical_querystring}\n"
                + f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
            )

        def sign(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        string_to_sign = (
            f"{algorithm}\n{amzdate}\n{credential_scope}\n"
            + hashlib.sha256(canonical_request().encode("utf-8")).hexdigest()
        )

        date_key = sign(("AWS4" + secret_access_key).encode("utf-8"), datestamp)
        region_key = sign(date_key, region)
        service_key = sign(region_key, service)
        request_key = sign(service_key, "aws4_request")
        return sign(request_key, string_to_sign).hex()

    return {
        **pre_auth_headers,
        "x-amz-date": amzdate,
        "x-amz-content-sha256": payload_hash,
        "Authorization": f"{algorithm} Credential={access_key_id}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature=" + signature(),
    }
