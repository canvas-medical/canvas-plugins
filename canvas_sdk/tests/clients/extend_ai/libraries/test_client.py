from dataclasses import dataclass
from http import HTTPStatus
from types import SimpleNamespace
from typing import Any, Self
from unittest.mock import MagicMock, call, patch

import pytest

from canvas_sdk.clients.extend_ai.constants import BaseProcessor, ParserChunking, ParserTarget
from canvas_sdk.clients.extend_ai.libraries.client import Client
from canvas_sdk.clients.extend_ai.structures import ProcessorMeta, RequestFailed, StoredFile
from canvas_sdk.clients.extend_ai.structures.config import (
    AdvancedOptionsExtraction,
    ConfigExtraction,
    Parser,
)
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


def test_init() -> None:
    """Test that Client initializes with the correct headers including API version and auth token."""
    tested = Client("test_key")
    assert tested.headers == {
        "x-extend-api-version": "2025-04-21",
        "Authorization": "Bearer test_key",
    }


@pytest.mark.parametrize(
    ("status_code", "json_response", "content_decode", "expected", "exp_calls"),
    [
        pytest.param(
            HTTPStatus.OK,
            {"success": True, "data": {"id": "123"}},
            None,
            "mock_result",
            [call.json(), call.from_dict({"id": "123"})],
            id="successful_response",
        ),
        pytest.param(
            HTTPStatus.BAD_REQUEST,
            None,
            "error message",
            RequestFailed(status_code=HTTPStatus.BAD_REQUEST, message="error message"),
            [call.content.decode()],
            id="failed_status_code",
        ),
        pytest.param(
            HTTPStatus.OK,
            {"success": False},
            "error message",
            RequestFailed(status_code=HTTPStatus.OK, message="error message"),
            [call.json(), call.content.decode()],
            id="failed_success_false",
        ),
    ],
)
@patch("canvas_sdk.clients.extend_ai.libraries.client.Response")
def test_valid_content(
    mock_response: MagicMock,
    status_code: Any,
    json_response: Any,
    content_decode: Any,
    expected: Any,
    exp_calls: list,
) -> None:
    """Test valid_content method handles successful responses and various failure cases."""
    mock_response.status_code = status_code
    mock_response.json.side_effect = [json_response]
    mock_response.content.decode.side_effect = [content_decode]
    mock_response.from_dict.side_effect = ["mock_result"]

    tested = Client
    result = tested.valid_content(mock_response, "data", mock_response)
    assert result == expected
    assert mock_response.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("responses", "expected", "exp_calls"),
    [
        pytest.param(
            [
                SimpleNamespace(
                    status_code=HTTPStatus.OK,
                    json=lambda: {
                        "success": True,
                        "items": [
                            {"id": "123", "name": "theName1"},
                            {"id": "456", "name": "theName2"},
                        ],
                    },
                )
            ],
            [
                ImplementedStructure(id=123, name="theName1"),
                ImplementedStructure(id=456, name="theName2"),
            ],
            [
                call("https://api.extend.ai"),
                call().get(
                    "/the/path",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer theKey",
                    },
                ),
            ],
            id="single_page_success",
        ),
        pytest.param(
            [
                SimpleNamespace(
                    status_code=HTTPStatus.OK,
                    json=lambda: {
                        "success": True,
                        "items": [
                            {"id": "123", "name": "theName1"},
                            {"id": "456", "name": "theName2"},
                        ],
                        "nextPageToken": "token123",
                    },
                ),
                SimpleNamespace(
                    status_code=HTTPStatus.OK,
                    json=lambda: {
                        "success": True,
                        "items": [{"id": "789", "name": "theName3"}],
                    },
                ),
            ],
            [
                ImplementedStructure(id=123, name="theName1"),
                ImplementedStructure(id=456, name="theName2"),
                ImplementedStructure(id=789, name="theName3"),
            ],
            [
                call("https://api.extend.ai"),
                call().get(
                    "/the/path",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer theKey",
                    },
                ),
                call().get(
                    "/the/path?nextPageToken=token123",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer theKey",
                    },
                ),
            ],
            id="multi_page_success",
        ),
        pytest.param(
            [
                SimpleNamespace(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content=b"error message",
                )
            ],
            RequestFailed(status_code=HTTPStatus.BAD_REQUEST, message="error message"),
            [
                call("https://api.extend.ai"),
                call().get(
                    "/the/path",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer theKey",
                    },
                ),
            ],
            id="failed_status_code",
        ),
        pytest.param(
            [
                SimpleNamespace(
                    status_code=HTTPStatus.OK,
                    json=lambda: {"success": False},
                    content=b"explanation message",
                )
            ],
            RequestFailed(status_code=HTTPStatus.OK, message="explanation message"),
            [
                call("https://api.extend.ai"),
                call().get(
                    "/the/path",
                    headers={
                        "x-extend-api-version": "2025-04-21",
                        "Authorization": "Bearer theKey",
                    },
                ),
            ],
            id="failed_success_false",
        ),
    ],
)
@patch("canvas_sdk.clients.extend_ai.libraries.client.Http")
def test_valid_content_list(
    mock_http: MagicMock, responses: list, expected: Any, exp_calls: list
) -> None:
    """Test valid_content_list method handles paginated responses and error cases."""
    mock_http.return_value.get.side_effect = responses

    tested = Client("theKey")
    result = tested.valid_content_list("/the/path", "items", ImplementedStructure)

    assert result == expected
    assert mock_http.mock_calls == exp_calls


@patch("canvas_sdk.clients.extend_ai.libraries.client.Client.valid_content_list")
def test_list_files(mock_valid_content_list: MagicMock) -> None:
    """Test list_files method calls valid_content_list with the correct parameters."""

    def reset_mocks() -> None:
        mock_valid_content_list.reset_mock()

    mock_valid_content_list.side_effect = ["theResponse"]

    tested = Client("test_key")
    result = tested.list_files()
    expected = "theResponse"
    assert result == expected  # type: ignore

    calls = [call("/files", "files", StoredFile)]
    assert mock_valid_content_list.mock_calls == calls
    reset_mocks()


@pytest.mark.parametrize(
    ("file_id", "status_code", "json_response", "content", "expected"),
    [
        pytest.param(
            "file123",
            HTTPStatus.OK,
            {"success": True},
            b"no error",
            True,
            id="successful_deletion",
        ),
        pytest.param(
            "file123",
            HTTPStatus.BAD_REQUEST,
            {},
            b"error message",
            RequestFailed(status_code=HTTPStatus.BAD_REQUEST, message="error message"),
            id="failed_deletion",
        ),
    ],
)
@patch("canvas_sdk.clients.extend_ai.libraries.client.requests_delete")
def test_delete_file(
    mock_requests_delete: MagicMock,
    file_id: str,
    status_code: Any,
    json_response: dict,
    content: bytes,
    expected: Any,
) -> None:
    """Test delete_file method handles successful deletion and error responses."""
    mock_requests_delete.side_effect = [
        SimpleNamespace(
            status_code=status_code,
            json=lambda: json_response,
            content=content,
        ),
    ]
    tested = Client("test_key")
    result = tested.delete_file(file_id)
    assert result == expected

    calls = [call(f"https://api.extend.ai/files/{file_id}", headers=tested.headers)]
    assert mock_requests_delete.mock_calls == calls


@patch("canvas_sdk.clients.extend_ai.libraries.client.Client.valid_content_list")
def test_list_processors(mock_valid_content_list: MagicMock) -> None:
    """Test list_processors method calls valid_content_list with the correct parameters."""

    def reset_mocks() -> None:
        mock_valid_content_list.reset_mock()

    mock_valid_content_list.side_effect = ["theResponse"]

    tested = Client("test_key")
    result = tested.list_processors()
    expected = "theResponse"
    assert result == expected  # type: ignore

    calls = [call("/processors", "processors", ProcessorMeta)]
    assert mock_valid_content_list.mock_calls == calls
    reset_mocks()


@pytest.mark.parametrize(
    ("processor_id", "version", "expected_path"),
    [
        pytest.param(
            "proc123",
            "theVersion",
            "/processors/proc123/versions/theVersion",
            id="with_version",
        ),
        pytest.param(
            "proc123",
            "",
            "/processors/proc123/versions/draft",
            id="empty_version_defaults_to_draft",
        ),
    ],
)
@patch.object(Client, "valid_content")
@patch("canvas_sdk.clients.extend_ai.libraries.client.Http")
def test_processor(
    mock_http: MagicMock,
    mock_valid_content: MagicMock,
    processor_id: str,
    version: str,
    expected_path: str,
) -> None:
    """Test processor method retrieves a specific processor version, defaulting to draft if empty."""
    mock_http.return_value.get.side_effect = ["theResponse"]
    mock_valid_content.side_effect = ["theProcessor"]

    tested = Client("test_key")
    result = tested.processor(processor_id, version)
    expected = "theProcessor"
    assert result == expected  # type: ignore

    calls = [
        call("https://api.extend.ai"),
        call().get(
            expected_path,
            headers={"x-extend-api-version": "2025-04-21", "Authorization": "Bearer test_key"},
        ),
    ]
    assert mock_http.mock_calls == calls


@patch.object(Client, "valid_content")
@patch("canvas_sdk.clients.extend_ai.libraries.client.Http")
def test_create_processor(mock_http: MagicMock, mock_valid_content: MagicMock) -> None:
    """Test create_processor method sends correct configuration data to the API."""
    config = ConfigExtraction(
        base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
        extraction_rule="Extract all",
        schema={"type": "object"},
        advanced_options=AdvancedOptionsExtraction(
            model_reasoning_insights_enabled=True,
            advanced_multimodal_enabled=False,
            citations_enabled=False,
            page_ranges=[],
        ),
        parser=Parser(
            target=ParserTarget.MARKDOWN,
            chunking_strategy=ParserChunking.PAGE,
        ),
    )

    mock_http.return_value.post.side_effect = ["theResponse"]
    mock_valid_content.side_effect = ["theProcessor"]

    tested = Client("test_key")
    result = tested.create_processor("Test Processor", config)
    expected = "theProcessor"
    assert result == expected  # type: ignore

    calls = [
        call("https://api.extend.ai"),
        call().post(
            "/processors",
            headers={
                "x-extend-api-version": "2025-04-21",
                "Authorization": "Bearer test_key",
                "Content-Type": "application/json",
            },
            json={
                "name": "Test Processor",
                "type": "EXTRACT",
                "config": {
                    "type": "EXTRACT",
                    "baseProcessor": "extraction_performance",
                    "extractionRule": "Extract all",
                    "schema": {"type": "object"},
                    "advancedOptions": {
                        "modelReasoningInsightsEnabled": True,
                        "advancedMultimodalEnabled": False,
                        "citationsEnabled": False,
                        "pageRanges": [],
                    },
                    "parser": {
                        "target": "markdown",
                        "chunkingStrategy": {"type": "page"},
                    },
                },
            },
        ),
    ]
    assert mock_http.mock_calls == calls


@patch.object(Client, "valid_content")
@patch("canvas_sdk.clients.extend_ai.libraries.client.Http")
def test_run_status(mock_http: MagicMock, mock_valid_content: MagicMock) -> None:
    """Test run_status method retrieves the status of a processor run."""
    mock_http.return_value.post.side_effect = ["theResponse"]
    mock_valid_content.side_effect = ["theProcessorRun"]

    tested = Client("test_key")
    result = tested.run_status("run123")
    expected = "theProcessorRun"
    assert result == expected  # type: ignore

    calls = [
        call("https://api.extend.ai"),
        call().get(
            "/processor_runs/run123",
            headers={
                "x-extend-api-version": "2025-04-21",
                "Authorization": "Bearer test_key",
            },
        ),
    ]
    assert mock_http.mock_calls == calls


@pytest.mark.parametrize(
    ("config", "expected_data"),
    [
        pytest.param(
            None,
            {
                "processorId": "proc123",
                "file": {
                    "fileName": "theFileName",
                    "fileUrl": "theFileUrl",
                },
            },
            id="without_config",
        ),
        pytest.param(
            ConfigExtraction(
                base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                extraction_rule="Extract all",
                schema={"type": "object"},
                advanced_options=AdvancedOptionsExtraction(
                    model_reasoning_insights_enabled=True,
                    advanced_multimodal_enabled=False,
                    citations_enabled=False,
                    page_ranges=[],
                ),
                parser=Parser(
                    target=ParserTarget.MARKDOWN,
                    chunking_strategy=ParserChunking.PAGE,
                ),
            ),
            {
                "processorId": "proc123",
                "file": {
                    "fileName": "theFileName",
                    "fileUrl": "theFileUrl",
                },
                "config": {
                    "type": "EXTRACT",
                    "baseProcessor": "extraction_performance",
                    "extractionRule": "Extract all",
                    "schema": {"type": "object"},
                    "advancedOptions": {
                        "modelReasoningInsightsEnabled": True,
                        "advancedMultimodalEnabled": False,
                        "citationsEnabled": False,
                        "pageRanges": [],
                    },
                    "parser": {
                        "target": "markdown",
                        "chunkingStrategy": {"type": "page"},
                    },
                },
            },
            id="with_config",
        ),
    ],
)
@patch.object(Client, "valid_content")
@patch("canvas_sdk.clients.extend_ai.libraries.client.Http")
def test_run_processor(
    mock_http: MagicMock, mock_valid_content: MagicMock, config: Any, expected_data: dict
) -> None:
    """Test run_processor method handles execution with and without optional config."""
    mock_http.return_value.post.side_effect = ["theResponse"]
    mock_valid_content.side_effect = ["theProcessorRun"]

    tested = Client("test_key")
    result = tested.run_processor("proc123", "theFileName", "theFileUrl", config)
    expected = "theProcessorRun"
    assert result == expected  # type: ignore

    calls = [
        call("https://api.extend.ai"),
        call().post(
            "/processor_runs",
            headers={
                "x-extend-api-version": "2025-04-21",
                "Authorization": "Bearer test_key",
                "Content-Type": "application/json",
            },
            json=expected_data,
        ),
    ]
    assert mock_http.mock_calls == calls
