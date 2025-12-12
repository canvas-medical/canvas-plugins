from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest
from requests import Response

from canvas_sdk.clients.aws.libraries.s3 import S3
from canvas_sdk.clients.aws.structures.credentials import Credentials
from canvas_sdk.clients.aws.structures.s3_item import S3Item


def test__querystring() -> None:
    """Test _querystring method generates proper URL-encoded query strings."""
    tests = [
        # No params
        (None, ""),
        # Empty dict
        ({}, ""),
        # Single param
        ({"key1": "value1"}, "key1=value1"),
        # Multiple params (sorted)
        ({"key2": "value2", "key1": "value1"}, "key1=value1&key2=value2"),
        # Special characters - changed
        ({"key": "value with spaces"}, "key=value%20with%20spaces"),
        # Special characters - unchanged
        ({"key": "value-with.characters_acceptable~"}, "key=value-with.characters_acceptable~"),
    ]
    tested = S3
    for params, expected in tests:
        result = tested._querystring(params)
        assert result == expected


def test__hmac_bytes() -> None:
    """Test _hmac_bytes method returns HMAC-SHA256 digest as bytes."""
    key = b"test_key"
    data = "test_data"
    tested = S3
    result = tested._hmac_bytes(key, data)
    expected = b"F\xa5\xb2{~fr'\x1c\x99\x8fMy\xedF\x0f\xf0<\x88\xca\xcd15_\xfc\x16\x159\xe1ex$"
    assert result == expected
    assert len(result) == 32  # SHA256 produces 32 bytes


def test__hmac_str() -> None:
    """Test _hmac_str method returns HMAC-SHA256 digest as hex string."""
    key = b"test_key"
    data = "test_data"
    tested = S3
    result = tested._hmac_str(key, data)
    expected = "46a5b27b7e6672271c998f4d79ed460ff03c88cacd31355ffc161539e1657824"
    assert result == expected
    assert len(result) == 64  # SHA256 hex produces 64 characters


@patch("canvas_sdk.clients.aws.libraries.s3.datetime")
def test__amz_date_time(mock_datetime: MagicMock) -> None:
    """Test _amz_date_time method returns current UTC time in AWS format."""
    mock_datetime.now.side_effect = [datetime(2025, 12, 1, 15, 7, 53, 123456, tzinfo=UTC)]
    tested = S3
    result = tested._amz_date_time()
    expected = "20251201T150753Z"
    assert result == expected
    calls = [call.now(UTC)]
    assert mock_datetime.mock_calls == calls


@pytest.mark.parametrize(
    ("amz_date_time", "expected"),
    [
        pytest.param("20251201T150753Z", "20251201", id="extract_date_20251201"),
        pytest.param("20250112T150753Z", "20250112", id="extract_date_20251212"),
    ],
)
def test__amz_date_from(amz_date_time: str, expected: str) -> None:
    """Test _amz_date_from method extracts date part from AWS datetime string."""
    tested = S3
    result = tested._amz_date_from(amz_date_time)
    assert result == expected


def test___init__() -> None:
    """Test __init__ method stores credentials."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )
    tested = S3(credentials)
    assert tested.credentials == credentials


@pytest.mark.parametrize(
    ("credentials", "expected"),
    [
        pytest.param(
            Credentials(key="theKey", secret="theSecret", region="theRegion", bucket="theBucket"),
            True,
            id="all_credentials_provided",
        ),
        pytest.param(
            Credentials(key="", secret="theSecret", region="theRegion", bucket="theBucket"),
            False,
            id="missing_key",
        ),
        pytest.param(
            Credentials(key="theKey", secret="", region="theRegion", bucket="theBucket"),
            False,
            id="missing_secret",
        ),
        pytest.param(
            Credentials(key="theKey", secret="theSecret", region="", bucket="theBucket"),
            False,
            id="missing_region",
        ),
        pytest.param(
            Credentials(key="theKey", secret="theSecret", region="theRegion", bucket=""),
            False,
            id="missing_bucket",
        ),
    ],
)
def test_is_ready(credentials: Credentials, expected: bool) -> None:
    """Test is_ready method validates all required credentials are present."""
    tested = S3(credentials)
    result = tested.is_ready()
    assert result is expected


def test__get_host() -> None:
    """Test _get_host method generates S3 endpoint hostname."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )

    tested = S3(credentials)
    result = tested._get_host()
    expected = "theBucket.s3.theRegion.amazonaws.com"
    assert result == expected


def test__get_signature_key() -> None:
    """Test _get_signature_key method generates AWS Signature V4 signing key and signature."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )
    tested = S3(credentials)

    credential_scope, signature = tested._get_signature_key(
        "20251201T121520Z", "theCanonicalRequest"
    )

    expected = "20251201/theRegion/s3/aws4_request"
    assert credential_scope == expected
    expected = "2628651da3fda37e48588e87e8e01022aac97686de2cfc463ee3b2beb038605b"
    assert signature == expected
    assert len(signature) == 64  # SHA256 hex


@patch.object(S3, "_headers_full")
def test__headers_with_params(mock_headers_full: MagicMock) -> None:
    """Test _headers_with_params method generates headers with query parameters."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )
    tested = S3(credentials)

    mock_headers_full.side_effect = [{"header": "value"}]
    result = tested._headers_with_params("file.txt", {"key": "value"})
    expected = {"header": "value"}
    assert result == expected

    calls = [call("file.txt", None, {"key": "value"})]
    assert mock_headers_full.mock_calls == calls


@patch.object(S3, "_headers_full")
def test__headers_with_data(mock_headers_full: MagicMock) -> None:
    """Test _headers_with_data method generates headers with data payload."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )
    tested = S3(credentials)

    mock_headers_full.side_effect = [{"header": "value"}]
    result = tested._headers_with_data("file.txt", (b"data", "text/plain"))
    expected = {"header": "value"}
    assert result == expected

    calls = [call("file.txt", (b"data", "text/plain"), None)]
    assert mock_headers_full.mock_calls == calls


@patch.object(S3, "_headers_full")
def test__headers(mock_headers_full: MagicMock) -> None:
    """Test _headers method generates headers for simple GET request."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )
    tested = S3(credentials)

    mock_headers_full.side_effect = [{"header": "value"}]
    result = tested._headers("file.txt")
    expected = {"header": "value"}
    assert result == expected

    calls = [call("file.txt", None, None)]
    assert mock_headers_full.mock_calls == calls


@pytest.mark.parametrize(
    ("object_key", "data", "params", "exp_signed", "exp_signature", "exp_sha256"),
    [
        pytest.param(
            "file.txt",
            None,
            None,
            "host",
            "d3308e8a1e18d272898efebcf9ef0e575738d9845c748ffae69818c830d01809",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            id="get_request_no_data",
        ),
        pytest.param(
            "file.txt",
            (b"content", "text/plain"),
            None,
            "content-type;host",
            "4326709b7dfd5f6a860f2e75a7ce4061f4c550da9ea9f18b526d78c063591c03",
            "ed7002b439e9ac845f22357d822bac1444730fbdb6016d3ec9432297b9ec9f73",
            id="put_request_with_data",
        ),
        pytest.param(
            "file.txt",
            None,
            {"key": "value"},
            "host",
            "f0a1ba5845600643d8c73c64d3f4d90a403279b14a7e9b90d452a3efd44a6112",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            id="get_request_with_params",
        ),
    ],
)
@patch.object(S3, "_amz_date_time")
def test__headers_full(
    mock_amz_date_time: MagicMock,
    object_key: str,
    data: Any,
    params: Any,
    exp_signed: str,
    exp_signature: str,
    exp_sha256: str,
) -> None:
    """Test _headers_full method generates complete AWS Signature V4 headers."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )
    tested = S3(credentials)
    mock_amz_date_time.side_effect = ["20251201T121543Z"]
    result = tested._headers_full(object_key, data, params)

    authorization = (
        "AWS4-HMAC-SHA256 Credential=theKey/20251201/theRegion/s3/aws4_request, "
        f"SignedHeaders={exp_signed};x-amz-content-sha256;x-amz-date, "
        f"Signature={exp_signature}"
    )

    expected = {
        "Authorization": authorization,
        "Host": "theBucket.s3.theRegion.amazonaws.com",
        "x-amz-content-sha256": exp_sha256,
        "x-amz-date": "20251201T121543Z",
    }
    assert result == expected
    calls = [call()]
    assert mock_amz_date_time.mock_calls == calls


@pytest.mark.parametrize(
    ("is_ready", "expect_response", "exp_headers_calls", "exp_http_calls"),
    [
        pytest.param(
            True,
            True,
            [call("path/to/file.txt")],
            [
                call("https://theHost/"),
                call().get(
                    url="path/to/file.txt", headers={"Host": "theHost", "Authorization": "..."}
                ),
            ],
            id="is_ready",
        ),
        pytest.param(
            False,
            False,
            [],
            [],
            id="not_is_ready",
        ),
    ],
)
@patch("canvas_sdk.clients.aws.libraries.s3.Http")
@patch.object(S3, "_headers")
@patch.object(S3, "is_ready")
def test_access_s3_object(
    mock_is_ready: MagicMock,
    mock_headers: MagicMock,
    mock_http: MagicMock,
    is_ready: bool,
    expect_response: bool,
    exp_headers_calls: list,
    exp_http_calls: list,
) -> None:
    """Test access_s3_object method downloads objects from S3."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )

    tested = S3(credentials)

    mock_is_ready.side_effect = [is_ready]
    mock_headers.side_effect = [{"Host": "theHost", "Authorization": "..."}]
    response = Response()
    mock_http.return_value.get.side_effect = [response]

    result = tested.access_s3_object("path/to/file.txt")
    if expect_response:
        assert result is response
    else:
        assert result is None

    calls = [call()]
    assert mock_is_ready.mock_calls == calls
    assert mock_headers.mock_calls == exp_headers_calls
    assert mock_http.mock_calls == exp_http_calls


@patch.object(S3, "upload_binary_to_s3")
def test_upload_text_to_s3(mock_upload_binary: MagicMock) -> None:
    """Test upload_text_to_s3 method uploads text data to S3."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )

    tested = S3(credentials)
    response = Response()
    mock_upload_binary.side_effect = [response]

    result = tested.upload_text_to_s3("file.txt", "Hello World")
    assert result is response

    calls = [call("file.txt", b"Hello World", "text/plain")]
    assert mock_upload_binary.mock_calls == calls


@pytest.mark.parametrize(
    ("is_ready", "expect_response", "exp_headers_calls", "exp_http_calls"),
    [
        pytest.param(
            True,
            True,
            [call("file.bin", (b"binary content", "application/octet-stream"))],
            [
                call("https://theHost/"),
                call().put(
                    url="file.bin",
                    headers={
                        "Host": "theHost",
                        "Authorization": "...",
                        "Content-Type": "application/octet-stream",
                        "Content-Length": "14",
                    },
                    data=b"binary content",
                ),
            ],
            id="is_ready",
        ),
        pytest.param(
            False,
            False,
            [],
            [],
            id="not_is_ready",
        ),
    ],
)
@patch("canvas_sdk.clients.aws.libraries.s3.Http")
@patch.object(S3, "_headers_with_data")
@patch.object(S3, "is_ready")
def test_upload_binary_to_s3(
    mock_is_ready: MagicMock,
    mock_headers_with_data: MagicMock,
    mock_http: MagicMock,
    is_ready: bool,
    expect_response: bool,
    exp_headers_calls: list,
    exp_http_calls: list,
) -> None:
    """Test upload_binary_to_s3 method uploads binary data to S3."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )

    tested = S3(credentials)

    # successful upload
    mock_is_ready.side_effect = [is_ready]
    mock_headers_with_data.side_effect = [{"Host": "theHost", "Authorization": "..."}]
    response = Response()
    mock_http.return_value.put.side_effect = [response]

    binary_data = b"binary content"
    result = tested.upload_binary_to_s3("file.bin", binary_data, "application/octet-stream")
    if expect_response:
        assert result is response
    else:
        assert result is None

    calls = [call()]
    assert mock_is_ready.mock_calls == calls
    assert mock_headers_with_data.mock_calls == exp_headers_calls
    assert mock_http.mock_calls == exp_http_calls


@pytest.mark.parametrize(
    (
        "is_ready",
        "expect_response",
        "expect_error",
        "exp_headers_calls",
        "exp_querystring_calls",
        "exp_http_calls",
    ),
    [
        pytest.param(
            True,
            True,
            False,
            [
                call("", {"list-type": 2, "prefix": "test"}),
                call("", {"list-type": 2, "prefix": "test", "continuation-token": "token123"}),
            ],
            [
                call({"list-type": 2, "prefix": "test"}),
                call({"list-type": 2, "prefix": "test", "continuation-token": "token123"}),
            ],
            [
                call("https://theHost1?theQueryString1"),
                call().get(url="", headers={"Host": "theHost1"}),
                call("https://theHost2?theQueryString2"),
                call().get(url="", headers={"Host": "theHost2"}),
            ],
            id="is_ready_no_error",
        ),
        pytest.param(
            False,
            False,
            False,
            [],
            [],
            [],
            id="not_is_ready",
        ),
        pytest.param(
            True,
            False,
            True,
            [call("", {"list-type": 2, "prefix": "test"})],
            [call({"list-type": 2, "prefix": "test"})],
            [
                call("https://theHost1?theQueryString1"),
                call().get(url="", headers={"Host": "theHost1"}),
            ],
            id="is_ready_with_error",
        ),
    ],
)
@patch("canvas_sdk.clients.aws.libraries.s3.Http")
@patch.object(S3, "_headers_with_params")
@patch.object(S3, "_querystring")
@patch.object(S3, "is_ready")
def test_list_s3_objects(
    mock_is_ready: MagicMock,
    mock_querystring: MagicMock,
    mock_headers_with_params: MagicMock,
    mock_http: MagicMock,
    is_ready: bool,
    expect_response: bool,
    expect_error: bool,
    exp_headers_calls: list,
    exp_querystring_calls: list,
    exp_http_calls: list,
) -> None:
    """Test list_s3_objects method lists all S3 objects with pagination support."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )

    tested = S3(credentials)
    responses_with_error = [SimpleNamespace(status_code=404, text="Access Denied")]
    responses_no_error = [
        SimpleNamespace(
            status_code=200,
            content=b"""<?xml version="1.0" encoding="UTF-8"?>
    <ListBucketResult>
        <IsTruncated>true</IsTruncated>
        <NextContinuationToken>token123</NextContinuationToken>
        <Contents>
            <Key>file1.txt</Key>
            <Size>1024</Size>
            <LastModified>2025-12-01T12:16:12.123Z</LastModified>
        </Contents>
        <Contents>
            <Key>file2.txt</Key>
            <Size>2048</Size>
            <LastModified>2025-12-02T13:07:41.456Z</LastModified>
        </Contents>
    </ListBucketResult>""",
        ),
        SimpleNamespace(
            status_code=200,
            content=b"""<?xml version="1.0" encoding="UTF-8"?>
    <ListBucketResult>
        <IsTruncated>false</IsTruncated>
        <Contents>
            <Key>file3.txt</Key>
            <Size>1750</Size>
            <LastModified>2025-12-02T13:23:11.789Z</LastModified>
        </Contents>
        <Contents>
            <Key>file4.txt</Key>
            <Comment>invalid key</Comment>
        </Contents>
    </ListBucketResult>""",
        ),
    ]
    expected = [
        S3Item(
            key="file1.txt",
            size=1024,
            last_modified=datetime(2025, 12, 1, 12, 16, 12, 123000, tzinfo=UTC),
        ),
        S3Item(
            key="file2.txt",
            size=2048,
            last_modified=datetime(2025, 12, 2, 13, 7, 41, 456000, tzinfo=UTC),
        ),
        S3Item(
            key="file3.txt",
            size=1750,
            last_modified=datetime(2025, 12, 2, 13, 23, 11, 789000, tzinfo=UTC),
        ),
    ]

    mock_is_ready.side_effect = [is_ready]
    mock_headers_with_params.side_effect = [{"Host": "theHost1"}, {"Host": "theHost2"}]
    mock_querystring.side_effect = ["theQueryString1", "theQueryString2"]
    if expect_error:
        mock_http.return_value.get.side_effect = responses_with_error
        with pytest.raises(Exception, match="S3 response status code 404 with body Access Denied"):
            tested.list_s3_objects("test")
    else:
        mock_http.return_value.get.side_effect = responses_no_error
        result = tested.list_s3_objects("test")
        if expect_response:
            assert result == expected
        else:
            assert result is None

    calls = [call()]
    assert mock_is_ready.mock_calls == calls
    assert mock_headers_with_params.mock_calls == exp_headers_calls
    assert mock_querystring.mock_calls == exp_querystring_calls
    assert mock_http.mock_calls == exp_http_calls


@pytest.mark.parametrize(
    (
        "is_ready",
        "expect_response",
        "exp_querystring_calls",
        "exp_amz_date_time_calls",
        "exp_get_signature_key_calls",
    ),
    [
        pytest.param(
            True,
            True,
            [
                call(
                    {
                        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
                        "X-Amz-Credential": "theKey/20251201/theRegion/s3/aws4_request",
                        "X-Amz-Date": "20251201T123456Z",
                        "X-Amz-Expires": "4321",
                        "X-Amz-SignedHeaders": "host",
                        "X-Amz-Content-Sha256": "UNSIGNED-PAYLOAD",
                        "X-Amz-Signature": "theSignature",
                    }
                ),
                call(
                    {
                        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
                        "X-Amz-Credential": "theKey/20251201/theRegion/s3/aws4_request",
                        "X-Amz-Date": "20251201T123456Z",
                        "X-Amz-Expires": "4321",
                        "X-Amz-SignedHeaders": "host",
                        "X-Amz-Content-Sha256": "UNSIGNED-PAYLOAD",
                        "X-Amz-Signature": "theSignature",
                    }
                ),
            ],
            [call()],
            [
                call(
                    "20251201T123456Z",
                    "GET\n/file.txt\ntheQueryString1\nhost:theBucket.s3.theRegion.amazonaws.com\n\nhost\nUNSIGNED-PAYLOAD",
                )
            ],
            id="is_ready",
        ),
        pytest.param(
            False,
            False,
            [],
            [],
            [],
            id="not_is_ready",
        ),
    ],
)
@patch.object(S3, "_get_signature_key")
@patch.object(S3, "_amz_date_time")
@patch.object(S3, "_querystring")
@patch.object(S3, "is_ready")
def test_generate_presigned_url(
    mock_is_ready: MagicMock,
    mock_querystring: MagicMock,
    mock_amz_date_time: MagicMock,
    mock_get_signature_key: MagicMock,
    is_ready: bool,
    expect_response: bool,
    exp_querystring_calls: list,
    exp_amz_date_time_calls: list,
    exp_get_signature_key_calls: list,
) -> None:
    """Test generate_presigned_url method creates temporary access URLs for S3 objects."""
    credentials = Credentials(
        key="theKey",
        secret="theSecret",
        region="theRegion",
        bucket="theBucket",
    )

    tested = S3(credentials)

    mock_is_ready.side_effect = [is_ready]
    mock_querystring.side_effect = ["theQueryString1", "theQueryString2"]
    mock_amz_date_time.side_effect = ["20251201T123456Z"]
    mock_get_signature_key.side_effect = [("theCredentialScope", "theSignature")]

    result = tested.generate_presigned_url("file.txt", 4321)
    expected = "https://theBucket.s3.theRegion.amazonaws.com/file.txt?theQueryString2"
    if expect_response:
        assert result == expected
    else:
        assert result is None

    calls = [call()]
    assert mock_is_ready.mock_calls == calls
    assert mock_querystring.mock_calls == exp_querystring_calls
    assert mock_amz_date_time.mock_calls == exp_amz_date_time_calls
    assert mock_get_signature_key.mock_calls == exp_get_signature_key_calls
