"""Tests for integration_task_explorer plugin."""

import uuid
from unittest.mock import Mock, patch

from integration_task_explorer.routes.integration_task_api import IntegrationTaskAPI

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.v1.data import IntegrationTask
from canvas_sdk.v1.data.integration_task import IntegrationTaskChannel, IntegrationTaskStatus


class DummyRequest:
    """A dummy request object for testing IntegrationTaskAPI."""

    def __init__(
        self,
        path: str = "/integration-tasks/patient123",
        path_params: dict | None = None,
        query_params: dict | None = None,
    ) -> None:
        self.path = path
        self.path_params = path_params or {}
        self.query_params = query_params or {}


class DummyEvent:
    """A dummy event object for testing API handlers."""

    def __init__(self, context: dict | None = None, target: str | None = None) -> None:
        self.context = context or {}
        self.target = target


def test_import_integration_task_api() -> None:
    """Test that IntegrationTaskAPI can be imported without errors."""
    assert IntegrationTaskAPI is not None
    assert hasattr(IntegrationTaskAPI, "PATH")
    assert hasattr(IntegrationTaskAPI, "get")


def test_integration_task_api_path_configuration() -> None:
    """Test that IntegrationTaskAPI has correct path configuration."""
    assert IntegrationTaskAPI.PATH == "/integration-tasks/<patient_id>"


class TestIntegrationTaskAPI:
    """Test suite for IntegrationTaskAPI endpoint."""

    def test_authenticate_returns_true(self) -> None:
        """Test authentication always succeeds for testing purposes."""
        dummy_context = {"method": "GET", "path": "/integration-tasks/patient123"}
        api = IntegrationTaskAPI(event=DummyEvent(context=dummy_context))

        mock_credentials = Mock()
        assert api.authenticate(mock_credentials) is True

    def test_get_returns_task_list(self) -> None:
        """Test GET endpoint returns list of tasks."""
        # Create mock task
        mock_task = Mock(spec=IntegrationTask)
        mock_task.id = uuid.uuid4()
        mock_task.status = IntegrationTaskStatus.UNREAD
        mock_task.type = "fax_document"
        mock_task.title = "Test Fax Document"
        mock_task.channel = IntegrationTaskChannel.FAX
        mock_task.patient_id = "patient123"
        mock_task.patient = Mock()
        mock_task.service_provider_id = None
        mock_task.service_provider = None
        mock_task.is_fax = True
        mock_task.is_pending = True
        mock_task.is_processed = False
        mock_task.has_error = False
        mock_task.is_junked = False

        # Create mock queryset
        mock_queryset = Mock()
        mock_queryset.all.return_value = mock_queryset
        mock_queryset.for_patient.return_value = mock_queryset
        mock_queryset.__iter__ = lambda self: iter([mock_task])
        mock_queryset.__getitem__ = lambda self, key: [mock_task]

        # Create API request
        request = DummyRequest(
            path="/integration-tasks/patient123",
            path_params={"patient_id": "patient123"},
            query_params={},
        )

        # Create API instance
        dummy_context = {"method": "GET", "path": "/integration-tasks/patient123"}
        api = IntegrationTaskAPI(event=DummyEvent(context=dummy_context))
        api.request = request

        with patch.object(IntegrationTask, "objects", mock_queryset):
            result = api.get()

            # Verify result
            assert len(result) == 1
            assert isinstance(result[0], JSONResponse)

    def test_get_with_status_filter(self) -> None:
        """Test GET endpoint applies status filter correctly."""
        mock_queryset = Mock()
        mock_queryset.all.return_value = mock_queryset
        mock_queryset.for_patient.return_value = mock_queryset
        mock_queryset.unread.return_value = mock_queryset
        mock_queryset.__iter__ = lambda self: iter([])
        mock_queryset.__getitem__ = lambda self, key: []

        # Create API request with status filter
        request = DummyRequest(
            path="/integration-tasks/patient123",
            path_params={"patient_id": "patient123"},
            query_params={"status": "unread"},
        )

        dummy_context = {"method": "GET", "path": "/integration-tasks/patient123"}
        api = IntegrationTaskAPI(event=DummyEvent(context=dummy_context))
        api.request = request

        with patch.object(IntegrationTask, "objects", mock_queryset):
            api.get()
            mock_queryset.unread.assert_called_once()

    def test_get_with_channel_filter(self) -> None:
        """Test GET endpoint applies channel filter correctly."""
        mock_queryset = Mock()
        mock_queryset.all.return_value = mock_queryset
        mock_queryset.for_patient.return_value = mock_queryset
        mock_queryset.faxes.return_value = mock_queryset
        mock_queryset.__iter__ = lambda self: iter([])
        mock_queryset.__getitem__ = lambda self, key: []

        # Create API request with channel filter
        request = DummyRequest(
            path="/integration-tasks/patient123",
            path_params={"patient_id": "patient123"},
            query_params={"channel": "fax"},
        )

        dummy_context = {"method": "GET", "path": "/integration-tasks/patient123"}
        api = IntegrationTaskAPI(event=DummyEvent(context=dummy_context))
        api.request = request

        with patch.object(IntegrationTask, "objects", mock_queryset):
            api.get()
            mock_queryset.faxes.assert_called_once()
