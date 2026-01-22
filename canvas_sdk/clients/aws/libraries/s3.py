from datetime import UTC, datetime
from hashlib import sha256
from hmac import new as hmac_new
from http import HTTPStatus
from re import DOTALL
from re import compile as re_compile
from re import search as re_search
from urllib.parse import quote

from requests import Response

from canvas_sdk.clients.aws.constants.s3 import S3 as Constants
from canvas_sdk.clients.aws.structures.credentials import Credentials
from canvas_sdk.clients.aws.structures.s3_item import S3Item
from canvas_sdk.utils.http import Http


class S3:
    """S3 client with signature V4 authentication.

    This class provides methods to interact with AWS S3 including:
    - Uploading and accessing objects
    - Listing objects with pagination
    - Generating presigned URLs
    """

    # Regex patterns for XML parsing in list operations
    _TRUNCATED_PATTERN = re_compile(r"<IsTruncated>(true|false)</IsTruncated>")
    _TOKEN_PATTERN = re_compile(r"<NextContinuationToken>(.*?)</NextContinuationToken>")
    _CONTENTS_PATTERN = re_compile(r"<Contents>(.*?)</Contents>", DOTALL)
    _KEY_PATTERN = r"<Key>(.*?)</Key>"
    _SIZE_PATTERN = r"<Size>(.*?)</Size>"
    _MODIFIED_PATTERN = r"<LastModified>(.*?)</LastModified>"

    @classmethod
    def _querystring(cls, params: dict | None) -> str:
        """Generate URL-encoded query string from parameters.

        Args:
            params: Dictionary of query parameters

        Returns:
            URL-encoded query string
        """
        result = ""
        if isinstance(params, dict):
            result = "&".join(
                [
                    f"{quote(k, safe=Constants.SAFE_CHARACTERS)}={quote(str(v), safe=Constants.SAFE_CHARACTERS)}"
                    for k, v in sorted(params.items())
                ],
            )
        return result

    @classmethod
    def _hmac_bytes(cls, key: bytes, data: str) -> bytes:
        """Compute HMAC-SHA256 and return as bytes.

        Args:
            key: Secret key as bytes
            data: Data to sign

        Returns:
            HMAC digest as bytes
        """
        return hmac_new(key, data.encode("utf-8"), sha256).digest()

    @classmethod
    def _hmac_str(cls, key: bytes, data: str) -> str:
        """Compute HMAC-SHA256 and return as hex string.

        Args:
            key: Secret key as bytes
            data: Data to sign

        Returns:
            HMAC digest as hexadecimal string
        """
        return hmac_new(key, data.encode("utf-8"), sha256).hexdigest()

    @classmethod
    def _amz_date_time(cls) -> str:
        """Get current UTC time in AWS date format.

        Returns:
            Current UTC time as YYYYMMDDTHHMMSSZ string
        """
        return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    @classmethod
    def _amz_date_from(cls, amz_date_time: str) -> str:
        """Extract date part from AWS datetime string.

        Args:
            amz_date_time: AWS datetime string (YYYYMMDDTHHMMSSZ)

        Returns:
            Date part (YYYYMMDD)
        """
        return amz_date_time[:8]

    def __init__(self, credentials: Credentials) -> None:
        """Initialize AWS S3 client with credentials.

        Args:
            credentials: AWS credentials for authentication
        """
        self.credentials = credentials

    def is_ready(self) -> bool:
        """Check if all required credentials are provided.

        Returns:
            True if all credentials are non-empty, False otherwise
        """
        return bool(
            self.credentials.key
            and self.credentials.secret
            and self.credentials.region
            and self.credentials.bucket
        )

    def _get_host(self) -> str:
        """Generate S3 endpoint hostname.

        Returns:
            S3 bucket endpoint hostname
        """
        return f"{self.credentials.bucket}.s3.{self.credentials.region}.amazonaws.com"

    def _get_signature_key(self, amz_date: str, canonical_request: str) -> tuple[str, str]:
        """Generate AWS Signature V4 signing key and signature.

        Args:
            amz_date: AWS date-time string
            canonical_request: Canonical request string to sign

        Returns:
            Tuple of (credential_scope, signature)
        """
        date_stamp = self._amz_date_from(amz_date)
        credential_scope = f"{date_stamp}/{self.credentials.region}/{Constants.SERVICE_NAME}/{Constants.REQUEST_TYPE}"

        k_secret = f"AWS4{self.credentials.secret}".encode()
        k_date = self._hmac_bytes(k_secret, date_stamp)
        k_region = self._hmac_bytes(k_date, self.credentials.region)
        k_service = self._hmac_bytes(k_region, Constants.SERVICE_NAME)
        k_signing = self._hmac_bytes(k_service, Constants.REQUEST_TYPE)
        string_to_sign = (
            f"{Constants.ALGORITHM}\n"
            f"{amz_date}\n"
            f"{credential_scope}\n"
            f"{sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )
        signature = self._hmac_str(k_signing, string_to_sign)

        return credential_scope, signature

    def _headers_with_params(self, object_key: str, params: dict) -> dict:
        """Generate headers for request with query parameters.

        Args:
            object_key: S3 object key
            params: Query parameters

        Returns:
            Request headers with AWS signature
        """
        return self._headers_full("GET", object_key, None, params)

    def _headers_with_data(self, object_key: str, data: tuple[bytes, str]) -> dict:
        """Generate headers for request with data payload.

        Args:
            object_key: S3 object key
            data: Tuple of (binary_data, content_type)

        Returns:
            Request headers with AWS signature
        """
        return self._headers_full("PUT", object_key, data, None)

    def _headers(self, object_key: str) -> dict:
        """Generate headers for simple GET request.

        Args:
            object_key: S3 object key

        Returns:
            Request headers with AWS signature
        """
        return self._headers_full("GET", object_key, None, None)

    def _headers_full(
        self,
        method: str,
        object_key: str,
        data: tuple[bytes, str] | None,
        params: dict | None,
    ) -> dict:
        """Generate complete AWS Signature V4 headers.

        Args:
            method: HTTP method (GET, PUT, DELETE, etc.)
            object_key: S3 object key
            data: Optional tuple of (binary_data, content_type)
            params: Optional query parameters

        Returns:
            Complete request headers with AWS signature
        """
        # Extract data if provided
        if data is None:
            binary_data, content_type = b"", ""
        else:
            binary_data, content_type = data

        # Generate base components
        host = self._get_host()
        amz_date = self._amz_date_time()
        payload_hash = sha256(binary_data).hexdigest()
        canonical_uri = f"/{quote(object_key)}"
        canonical_querystring = self._querystring(params)

        # Build canonical headers and signed headers list
        headers_list = []
        signed_headers_list = []

        if content_type:
            headers_list.append(f"content-type:{content_type}")
            signed_headers_list.append("content-type")

        headers_list.extend(
            [
                f"host:{host}",
                f"x-amz-content-sha256:{payload_hash}",
                f"x-amz-date:{amz_date}",
            ]
        )
        signed_headers_list.extend(["host", "x-amz-content-sha256", "x-amz-date"])

        canonical_headers = "\n".join(headers_list) + "\n"
        signed_headers = ";".join(signed_headers_list)

        # Create canonical request
        canonical_request = (
            f"{method}\n"
            f"{canonical_uri}\n"
            f"{canonical_querystring}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{payload_hash}"
        )

        # Generate signature
        credential_scope, signature = self._get_signature_key(amz_date, canonical_request)
        authorization_header = (
            f"{Constants.ALGORITHM} Credential={self.credentials.key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        result = {
            "Host": host,
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
            "Authorization": authorization_header,
        }
        return result

    def access_s3_object(self, object_key: str) -> Response | None:
        """Access (download) an object from S3.

        Args:
            object_key: S3 object key to access

        Returns:
            HTTP response containing the object data
        """
        if not self.is_ready():
            return None
        headers = self._headers(object_key)
        endpoint = f"https://{headers['Host']}/"
        return Http(endpoint).get(url=object_key, headers=headers)

    def upload_text_to_s3(self, object_key: str, data: str) -> Response | None:
        """Upload text data to S3 as text/plain.

        Args:
            object_key: S3 object key to create/update
            data: Text data to upload

        Returns:
            HTTP response from S3
        """
        return self.upload_binary_to_s3(object_key, data.encode(), "text/plain")

    def upload_binary_to_s3(
        self,
        object_key: str,
        binary_data: bytes,
        content_type: str,
    ) -> Response | None:
        """Upload binary data to S3.

        Args:
            object_key: S3 object key to create/update
            binary_data: Binary data to upload
            content_type: MIME type of the data

        Returns:
            HTTP response from S3
        """
        if not self.is_ready():
            return None
        headers = self._headers_with_data(object_key, (binary_data, content_type)) | {
            "Content-Type": content_type,
            "Content-Length": str(len(binary_data)),
        }
        endpoint = f"https://{headers['Host']}/"
        return Http(endpoint).put(url=object_key, headers=headers, data=binary_data)

    def delete_object(self, object_key: str) -> Response | None:
        """Delete an object from S3.

        Args:
            object_key: S3 object key to delete

        Returns:
            HTTP response from S3, or None if credentials not ready
        """
        if not self.is_ready():
            return None
        headers = self._headers_full("DELETE", object_key, None, None)
        endpoint = f"https://{headers['Host']}/"
        return Http(endpoint).delete(url=object_key, headers=headers)

    def list_s3_objects(self, prefix: str) -> list[S3Item] | None:
        """List all objects in S3 with given prefix.

        Handles pagination automatically to retrieve all matching objects.

        Args:
            prefix: S3 key prefix to filter objects

        Returns:
            List of AwsS3Item objects with metadata

        Raises:
            Exception: If S3 returns non-200 status code
        """
        if not self.is_ready():
            return None

        result: list[S3Item] = []
        continuation_token: str | None = None

        is_truncated = True
        while is_truncated:
            params: dict[str, int | str] = {
                "list-type": 2,
                "prefix": prefix,
            }
            if continuation_token:
                params["continuation-token"] = continuation_token

            headers = self._headers_with_params("", params)
            endpoint = f"https://{headers['Host']}?{self._querystring(params)}"
            response = Http(endpoint).get(url="", headers=headers)
            if response.status_code != HTTPStatus.OK.value:
                raise Exception(
                    f"S3 response status code {response.status_code} with body {response.text}"
                )

            response_text = response.content.decode("utf-8")
            for content_match in self._CONTENTS_PATTERN.finditer(response_text):
                content_xml = content_match.group(1)
                key_match = re_search(self._KEY_PATTERN, content_xml)
                size_match = re_search(self._SIZE_PATTERN, content_xml)
                modified_match = re_search(self._MODIFIED_PATTERN, content_xml)

                if key_match and size_match and modified_match:
                    result.append(
                        S3Item(
                            key=key_match.group(1),
                            size=int(size_match.group(1)),
                            last_modified=datetime.fromisoformat(modified_match.group(1)),
                        )
                    )

            truncated_match = self._TRUNCATED_PATTERN.search(response_text)
            is_truncated = bool(truncated_match and truncated_match.group(1) == "true")

            if is_truncated and (token_match := self._TOKEN_PATTERN.search(response_text)):
                continuation_token = token_match.group(1)

        return result

    def generate_presigned_url(self, object_key: str, expiration: int) -> str | None:
        """Generate a presigned URL for temporary access to S3 object.

        Args:
            object_key: S3 object key
            expiration: URL expiration time in seconds

        Returns:
            Presigned URL string, or empty string if not ready
        """
        if not self.is_ready():
            return None

        method = "GET"
        host = self._get_host()
        amz_date = self._amz_date_time()
        payload_hash = Constants.UNSIGNED_PAYLOAD
        canonical_uri = f"/{quote(object_key)}"
        canonical_headers = f"host:{host}\n"
        signed_headers = "host"
        credentials = [
            self.credentials.key,
            self._amz_date_from(amz_date),
            self.credentials.region,
            Constants.SERVICE_NAME,
            Constants.REQUEST_TYPE,
        ]

        params = {
            "X-Amz-Algorithm": Constants.ALGORITHM,
            "X-Amz-Credential": "/".join(credentials),
            "X-Amz-Date": amz_date,
            "X-Amz-Expires": str(expiration),
            "X-Amz-SignedHeaders": signed_headers,
            "X-Amz-Content-Sha256": payload_hash,
        }
        canonical_querystring = self._querystring(params)
        canonical_request = (
            f"{method}\n"
            f"{canonical_uri}\n"
            f"{canonical_querystring}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{payload_hash}"
        )

        _, signature = self._get_signature_key(amz_date, canonical_request)
        params["X-Amz-Signature"] = signature

        querystring = self._querystring(params)
        result = f"https://{host}/{quote(object_key)}?{querystring}"

        return result


__exports__ = ("S3",)
