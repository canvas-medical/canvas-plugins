from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace
from typing import Any, Self
from unittest.mock import Mock, call, patch

import pytest

from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.constants.run_status import RunStatus
from canvas_sdk.clients.extend_ai.libraries.client import Client
from canvas_sdk.clients.extend_ai.structures.config.config_base import ConfigBase
from canvas_sdk.clients.extend_ai.structures.processor_meta import ProcessorMeta
from canvas_sdk.clients.extend_ai.structures.processor_run import ProcessorRun
from canvas_sdk.clients.extend_ai.structures.processor_version import ProcessorVersion
from canvas_sdk.clients.extend_ai.structures.request_failed import RequestFailed
from canvas_sdk.clients.extend_ai.structures.stored_file import StoredFile
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass
class ImplementedStructure(Structure):
    """Concrete implementation of Structure for testing purposes."""

    id: int
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create an ImplementedStructure instance from a dictionary for testing."""
        return cls(id=int(data.get("id") or "0"), name=data.get("name") or "")

    def to_dict(self) -> dict:
        """Convert this ImplementedStructure to a dictionary for testing."""
        return {"id": self.id, "name": self.name}


@dataclass(frozen=True)
class MockConfig(ConfigBase):
    """Mock configuration for testing."""

    field: str

    @classmethod
    def processor_type(cls) -> ProcessorType:
        """Return extraction processor type."""
        return ProcessorType.EXTRACT

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create from dictionary."""
        return cls(field=data["field"])

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"field": self.field}


def test_init() -> None:
    """Test that Client initializes with the correct headers including API version and auth token."""
    tested = Client("test_key")
    assert tested.headers == {
        "x-extend-api-version": "2025-04-21",
        "Authorization": "Bearer test_key",
    }


@pytest.mark.parametrize(
    ("status_code", "response_json", "key", "expected"),
    [
        pytest.param(
            HTTPStatus.OK,
            {"success": True, "data": {"id": 1, "name": "test"}},
            "data",
            ImplementedStructure(id=1, name="test"),
            id="success",
        ),
    ],
)
def test__valid_content__success(
    status_code: int,
    response_json: dict,
    key: str,
    expected: ImplementedStructure,
) -> None:
    """Test _valid_content successfully extracts and instantiates data from valid responses."""
    mock_response = SimpleNamespace(
        status_code=status_code,
        json=lambda: response_json,
    )

    tested = Client
    result = tested._valid_content(mock_response, key, ImplementedStructure)  # type: ignore[arg-type]

    assert result == expected


@pytest.mark.parametrize(
    ("status_code", "response_json", "content", "key", "exp_calls"),
    [
        pytest.param(
            HTTPStatus.BAD_REQUEST,
            {"success": False, "error": "Bad request"},
            b"Bad request",
            "data",
            [call.content.decode()],  # Non-200 status short-circuits, only calls content.decode
            id="non_200_status",
        ),
        pytest.param(
            HTTPStatus.OK,
            {"success": False, "error": "Failed"},
            b"Failed",
            "data",
            [call.json(), call.content.decode()],  # 200 status but success=False
            id="success_false",
        ),
    ],
)
def test__valid_content__failure(
    status_code: int,
    response_json: dict,
    content: bytes,
    key: str,
    exp_calls: list,
) -> None:
    """Test _valid_content raises RequestFailed for non-successful responses."""
    mock_response = SimpleNamespace(
        status_code=status_code,
        json=lambda: response_json,
        content=SimpleNamespace(decode=lambda: content.decode()),
    )

    tested = Client
    with pytest.raises(RequestFailed) as exc_info:
        tested._valid_content(mock_response, key, ImplementedStructure)  # type: ignore[arg-type]

    assert exc_info.value.status_code == status_code
    assert exc_info.value.message == content.decode()


@pytest.mark.parametrize(
    ("responses", "expected", "exp_calls"),
    [
        pytest.param(
            [
                {
                    "status_code": HTTPStatus.OK,
                    "json": {
                        "success": True,
                        "items": [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}],
                    },
                }
            ],
            [ImplementedStructure(id=1, name="item1"), ImplementedStructure(id=2, name="item2")],
            [
                call(
                    "/test",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer test_key",
                    },
                )
            ],
            id="single_page",
        ),
        pytest.param(
            [
                {
                    "status_code": HTTPStatus.OK,
                    "json": {
                        "success": True,
                        "items": [{"id": 1, "name": "item1"}],
                        "nextPageToken": "token123",
                    },
                },
                {
                    "status_code": HTTPStatus.OK,
                    "json": {
                        "success": True,
                        "items": [{"id": 2, "name": "item2"}],
                    },
                },
            ],
            [ImplementedStructure(id=1, name="item1"), ImplementedStructure(id=2, name="item2")],
            [
                call(
                    "/test",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer test_key",
                    },
                ),
                call(
                    "/test?nextPageToken=token123",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer test_key",
                    },
                ),
            ],
            id="multiple_pages",
        ),
    ],
)
def test__valid_content_list__success(
    responses: list[dict],
    expected: list[Any],
    exp_calls: list[Any],
) -> None:
    """Test _valid_content_list correctly handles paginated responses."""
    tested = Client("test_key")
    mock_http_get = Mock()

    mock_responses = []
    for resp_data in responses:
        mock_resp = SimpleNamespace(
            status_code=resp_data["status_code"],
            json=lambda d=resp_data["json"]: d,
        )
        mock_responses.append(mock_resp)

    mock_http_get.side_effect = mock_responses

    with patch.object(tested.http, "get", mock_http_get):
        result = list(tested._valid_content_list("/test", "items", ImplementedStructure))

    assert result == expected

    assert mock_http_get.mock_calls == exp_calls


def test__valid_content_list__failure() -> None:
    """Test _valid_content_list raises RequestFailed on error response."""
    tested = Client("test_key")
    mock_http_get = Mock()

    mock_http_get.side_effect = [
        SimpleNamespace(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            json=lambda: {"success": False},
            content=SimpleNamespace(decode=lambda: "Server error"),
        )
    ]

    with patch.object(tested.http, "get", mock_http_get), pytest.raises(RequestFailed) as exc_info:
        list(tested._valid_content_list("/test", "items", ImplementedStructure))

    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.message == "Server error"
    exp_http_get_calls = [
        call(
            "/test",
            headers={"x-extend-api-version": "2025-04-21", "Authorization": "Bearer test_key"},
        ),
    ]
    assert mock_http_get.mock_calls == exp_http_get_calls


def test_list_files() -> None:
    """Test list_files delegates to _valid_content_list with correct parameters."""
    tested = Client("test_key")
    mock_valid_content_list = Mock()

    expected_files = [
        StoredFile(id="file1", type="pdf", name="doc1.pdf"),
        StoredFile(id="file2", type="png", name="img.png"),
    ]
    mock_valid_content_list.side_effect = [iter(expected_files)]

    with patch.object(tested, "_valid_content_list", mock_valid_content_list):
        result = list(tested.list_files())

    assert result == expected_files
    exp_calls = [call("/files", "files", StoredFile)]
    assert mock_valid_content_list.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("file_id", "status_code", "response_json", "expected"),
    [
        pytest.param(
            "file123",
            HTTPStatus.OK,
            {"success": True},
            True,
            id="success",
        ),
    ],
)
def test_delete_file__success(
    file_id: str,
    status_code: int,
    response_json: dict,
    expected: bool,
) -> None:
    """Test delete_file successfully deletes file and returns True."""
    tested = Client("test_key")

    with patch("canvas_sdk.clients.extend_ai.libraries.client.requests_delete") as mock_delete:
        mock_delete.side_effect = [
            SimpleNamespace(
                status_code=status_code,
                json=lambda: response_json,
            )
        ]

        result = tested.delete_file(file_id)

        assert result is expected
        exp_calls = [
            call(
                f"https://api.extend.ai/files/{file_id}",
                headers={"x-extend-api-version": "2025-04-21", "Authorization": "Bearer test_key"},
            ),
        ]
        assert mock_delete.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("file_id", "status_code", "content"),
    [
        pytest.param(
            "file123",
            HTTPStatus.NOT_FOUND,
            b"File not found",
            id="not_found",
        ),
        pytest.param(
            "file456",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            b"Server error",
            id="server_error",
        ),
    ],
)
def test_delete_file__failure(file_id: str, status_code: int, content: bytes) -> None:
    """Test delete_file raises RequestFailed on error responses."""
    tested = Client("test_key")

    with patch("canvas_sdk.clients.extend_ai.libraries.client.requests_delete") as mock_delete:
        mock_delete.side_effect = [
            SimpleNamespace(
                status_code=status_code,
                content=SimpleNamespace(decode=lambda: content.decode()),
            )
        ]

        with pytest.raises(RequestFailed) as exc_info:
            tested.delete_file(file_id)

    assert exc_info.value.status_code == status_code
    assert exc_info.value.message == content.decode()
    exp_delete_calls = [
        call(
            f"https://api.extend.ai/files/{file_id}",
            headers={"x-extend-api-version": "2025-04-21", "Authorization": "Bearer test_key"},
        ),
    ]
    assert mock_delete.mock_calls == exp_delete_calls


def test_list_processors() -> None:
    """Test list_processors delegates to _valid_content_list with correct parameters."""
    tested = Client("test_key")
    mock_valid_content_list = Mock()

    expected_processors = [
        ProcessorMeta(
            id="proc1",
            name="Processor 1",
            type=ProcessorType.EXTRACT,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
        ),
    ]
    mock_valid_content_list.side_effect = [iter(expected_processors)]

    with patch.object(tested, "_valid_content_list", mock_valid_content_list):
        result = list(tested.list_processors())

    assert result == expected_processors
    exp_calls = [call("/processors", "processors", ProcessorMeta)]
    assert mock_valid_content_list.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("processor_id", "version", "expected_version", "expected_url"),
    [
        pytest.param(
            "proc123",
            "v1.0",
            "v1.0",
            "/processors/proc123/versions/v1.0",
            id="with_version",
        ),
        pytest.param(
            "proc456",
            "",
            "draft",
            "/processors/proc456/versions/draft",
            id="empty_version_defaults_to_draft",
        ),
    ],
)
def test_processor(
    processor_id: str,
    version: str,
    expected_version: str,
    expected_url: str,
) -> None:
    """Test processor retrieves processor version details and defaults to draft when version is empty."""
    from datetime import datetime

    tested = Client("test_key")
    mock_http_get = Mock()
    mock_valid_content = Mock()

    mock_response = SimpleNamespace()
    mock_http_get.side_effect = [SimpleNamespace()]

    expected_processor_version = ProcessorVersion(
        id="version123",
        version=expected_version,
        description="Test processor version",
        processor=ProcessorMeta(
            id=processor_id,
            name="Test Processor",
            type=ProcessorType.EXTRACT,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
        ),
        config=MockConfig(field="test"),  # type: ignore[arg-type]
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
    )
    mock_valid_content.return_value = expected_processor_version

    with (
        patch.object(tested.http, "get", mock_http_get),
        patch.object(tested, "_valid_content", mock_valid_content),
    ):
        result = tested.processor(processor_id, version)

    assert result == expected_processor_version
    exp_http_calls = [
        call(
            expected_url,
            headers={"x-extend-api-version": "2025-04-21", "Authorization": "Bearer test_key"},
        )
    ]
    assert mock_http_get.mock_calls == exp_http_calls
    exp_valid_calls = [call(mock_response, "version", ProcessorVersion)]
    assert mock_valid_content.mock_calls == exp_valid_calls


def test_create_processor() -> None:
    """Test create_processor sends correct request with processor configuration."""
    from datetime import datetime

    client = Client("test_key")
    mock_http_post = Mock()
    mock_valid_content = Mock()

    mock_response = SimpleNamespace()
    mock_http_post.side_effect = [mock_response]

    config = MockConfig(field="test_value")
    expected_processor = ProcessorMeta(
        id="proc123",
        name="New Processor",
        type=ProcessorType.EXTRACT,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
    )
    mock_valid_content.return_value = expected_processor

    with (
        patch.object(client.http, "post", mock_http_post),
        patch.object(client, "_valid_content", mock_valid_content),
    ):
        result = client.create_processor("New Processor", config)

    assert result == expected_processor
    exp_http_calls = [
        call(
            "/processors",
            headers={
                "x-extend-api-version": "2025-04-21",
                "Authorization": "Bearer test_key",
                "Content-Type": "application/json",
            },
            json={
                "name": "New Processor",
                "type": "EXTRACT",
                "config": {"field": "test_value"},
            },
        )
    ]
    assert mock_http_post.mock_calls == exp_http_calls
    exp_valid_calls = [call(mock_response, "processor", ProcessorMeta)]
    assert mock_valid_content.mock_calls == exp_valid_calls


def test_run_status() -> None:
    """Test run_status retrieves processor run status."""
    tested = Client("test_key")
    mock_http_get = Mock()
    mock_valid_content = Mock()

    mock_response = SimpleNamespace()
    mock_http_get.side_effect = [mock_response]

    expected_run = ProcessorRun(
        id="run123",
        processor=ProcessorMeta(
            id="proc123",
            name="Test Processor",
            type=ProcessorType.EXTRACT,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
        ),
        output=None,
        status=RunStatus.PROCESSING,
        files=[],
        usage=0,
    )
    mock_valid_content.return_value = expected_run

    with (
        patch.object(tested.http, "get", mock_http_get),
        patch.object(tested, "_valid_content", mock_valid_content),
    ):
        result = tested.run_status("run123")

    assert result == expected_run
    exp_http_calls = [
        call(
            "/processor_runs/run123",
            headers={"x-extend-api-version": "2025-04-21", "Authorization": "Bearer test_key"},
        )
    ]
    assert mock_http_get.mock_calls == exp_http_calls
    exp_valid_calls = [call(mock_response, "processorRun", ProcessorRun)]
    assert mock_valid_content.mock_calls == exp_valid_calls


@pytest.mark.parametrize(
    ("processor_id", "file_name", "file_url", "config", "expected_data"),
    [
        pytest.param(
            "proc123",
            "document.pdf",
            "https://example.com/doc.pdf",
            None,
            {
                "processorId": "proc123",
                "file": {
                    "fileName": "document.pdf",
                    "fileUrl": "https://example.com/doc.pdf",
                },
            },
            id="without_config",
        ),
        pytest.param(
            "proc456",
            "image.png",
            "https://example.com/img.png",
            MockConfig(field="test"),
            {
                "processorId": "proc456",
                "file": {
                    "fileName": "image.png",
                    "fileUrl": "https://example.com/img.png",
                },
                "config": {"field": "test"},
            },
            id="with_config",
        ),
    ],
)
def test_run_processor(
    processor_id: str,
    file_name: str,
    file_url: str,
    config: MockConfig | None,
    expected_data: dict,
) -> None:
    """Test run_processor executes processor with correct parameters and optional config."""
    tested = Client("test_key")
    mock_http_post = Mock()
    mock_valid_content = Mock()

    mock_response = SimpleNamespace()
    mock_http_post.side_effect = [mock_response]

    expected_run = ProcessorRun(
        id="run123",
        processor=ProcessorMeta(
            id=processor_id,
            name="Test Processor",
            type=ProcessorType.EXTRACT,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
        ),
        output=None,
        status=RunStatus.PROCESSING,
        files=[],
        usage=0,
    )
    mock_valid_content.return_value = expected_run

    with (
        patch.object(tested.http, "post", mock_http_post),
        patch.object(tested, "_valid_content", mock_valid_content),
    ):
        result = tested.run_processor(processor_id, file_name, file_url, config)  # type: ignore[arg-type]

    assert result == expected_run
    exp_http_calls = [
        call(
            "/processor_runs",
            headers={
                "x-extend-api-version": "2025-04-21",
                "Authorization": "Bearer test_key",
                "Content-Type": "application/json",
            },
            json=expected_data,
        )
    ]
    assert mock_http_post.mock_calls == exp_http_calls
    exp_valid_calls = [call(mock_response, "processorRun", ProcessorRun)]
    assert mock_valid_content.mock_calls == exp_valid_calls
