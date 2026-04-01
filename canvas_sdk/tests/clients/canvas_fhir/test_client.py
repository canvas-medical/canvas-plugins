from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.clients.canvas_fhir import CanvasFhir
from settings import CUSTOMER_IDENTIFIER

MOCK_CREDENTIALS = {
    "access_token": "test_token",
    "expires_in": 3600,
    "refresh_token": "test_refresh",
    "scope": "test_scope",
    "token_type": "Bearer",
}


@pytest.fixture
def mock_get_cache() -> Generator[MagicMock, None, None]:
    """Mock the get_cache method of the CanvasFhir instance."""
    with patch("canvas_sdk.clients.canvas_fhir.client.get_cache") as mock:
        yield mock


@pytest.fixture
def mock_post() -> Generator[MagicMock, None, None]:
    """Mock the post method of the Http instance."""
    with patch("canvas_sdk.utils.http.Http.post") as mock:
        yield mock


@pytest.fixture
def mock_get() -> Generator[MagicMock, None, None]:
    """Mock the get method of the Http instance."""
    with patch("canvas_sdk.utils.http.Http.get") as mock:
        yield mock


@pytest.fixture
def mock_put() -> Generator[MagicMock, None, None]:
    """Mock the put method of the Http instance."""
    with patch("canvas_sdk.utils.http.Http.put") as mock:
        yield mock


@pytest.fixture
def client(mock_get_cache: MagicMock) -> CanvasFhir:
    """Return a CanvasFhir client with mocked credentials."""
    mock_get_cache.return_value.get.return_value = MOCK_CREDENTIALS
    return CanvasFhir(client_id="test", client_secret="test")


def test__api_base_url(client: CanvasFhir) -> None:
    """Test the defined URL of the CanvasFhir instance."""
    assert client._base_url == f"https://fumage-{CUSTOMER_IDENTIFIER}.canvasmedical.com"


def test__get_credentials_without_cached_credentials(
    mock_get_cache: MagicMock, mock_post: MagicMock
) -> None:
    """Test the _get_credentials method of the CanvasFhir instance without cached credentials."""
    mock_get_cache.return_value.get.return_value = None
    mock_post.return_value = MagicMock(status_code=200, json=lambda: MOCK_CREDENTIALS)

    tested = CanvasFhir(client_id="test", client_secret="test")
    result = tested._get_credentials()
    expected = MOCK_CREDENTIALS
    assert result == expected


def test__get_credentials_with_cached_credentials(
    mock_get_cache: MagicMock, mock_post: MagicMock
) -> None:
    """Test the _get_credentials method of the CanvasFhir instance with cached credentials."""
    mock_get_cache.return_value.get.return_value = MOCK_CREDENTIALS

    tested = CanvasFhir(client_id="test", client_secret="test")
    result = tested._get_credentials()
    expected = MOCK_CREDENTIALS

    mock_post.assert_not_called()
    assert result == expected


def test_create(client: CanvasFhir, mock_post: MagicMock) -> None:
    """Test creating a FHIR resource."""
    expected = {"resourceType": "Coverage", "id": "cov-123", "status": "active"}
    mock_post.return_value = MagicMock(status_code=201, json=lambda: expected)

    result = client.create("Coverage", {"resourceType": "Coverage", "status": "active"})

    assert result == expected
    mock_post.assert_called_once_with(
        f"{client._base_url}/Coverage",
        headers=client._get_headers(),
        json={"resourceType": "Coverage", "status": "active"},
    )


def test_read(client: CanvasFhir, mock_get: MagicMock) -> None:
    """Test reading a FHIR resource."""
    expected = {"resourceType": "AllergyIntolerance", "id": "allergy-123"}
    mock_get.return_value = MagicMock(status_code=200, json=lambda: expected)

    result = client.read("AllergyIntolerance", "allergy-123")

    assert result == expected
    mock_get.assert_called_once_with(
        f"{client._base_url}/AllergyIntolerance/allergy-123",
        headers=client._get_headers(),
    )


def test_search(client: CanvasFhir, mock_get: MagicMock) -> None:
    """Test searching for FHIR resources."""
    expected = {"resourceType": "Bundle", "entry": []}
    mock_get.return_value = MagicMock(status_code=200, json=lambda: expected)

    result = client.search("AllergyIntolerance", {"patient": "Patient/abc123"})

    assert result == expected
    mock_get.assert_called_once_with(
        f"{client._base_url}/AllergyIntolerance?patient=Patient%2Fabc123",
        headers=client._get_headers(),
    )


def test_update(client: CanvasFhir, mock_put: MagicMock) -> None:
    """Test updating a FHIR resource."""
    data = {"resourceType": "Coverage", "id": "cov-123", "status": "cancelled"}
    mock_put.return_value = MagicMock(status_code=200, json=lambda: data)

    result = client.update("Coverage", "cov-123", data)

    assert result == data
    mock_put.assert_called_once_with(
        f"{client._base_url}/Coverage/cov-123",
        headers=client._get_headers(),
        json=data,
    )
