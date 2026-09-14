"""Tests for charting_api_examples.routes.notes module."""

import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from charting_api_examples.routes.notes import NoteAPI


def create_api_instance(method="GET", path="/notes/"):
    """Helper function to create a NoteAPI instance with the specified HTTP method."""
    event = MagicMock()
    event.context = {
        "absolute_uri": "http://test.com/notes/",
        "method": method,
        "path": path,
    }
    return NoteAPI(event=event)


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = MagicMock()
    request.query_params = {}
    request.path_params = {}
    return request


@pytest.fixture
def mock_note():
    """Create a mock note object."""
    note = MagicMock()
    note.id = "note-123"
    note.patient.id = "patient-123"
    note.provider.id = "provider-123"
    note.datetime_of_service = "2025-01-15 10:00:00"
    note.note_type_version.id = "type-123"
    note.note_type_version.name = "Progress Note"
    note.note_type_version.display = "Progress Note"
    note.note_type_version.code = "progress"
    note.note_type_version.system = "http://example.com"
    return note


class TestNoteAPI:
    """Tests for NoteAPI class."""

    def test_prefix_configuration(self):
        """Test that the API prefix is correctly configured."""
        assert NoteAPI.PREFIX == "/notes"

    def test_api_inherits_from_expected_classes(self):
        """Test that NoteAPI inherits from the correct base classes."""
        from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI

        assert issubclass(NoteAPI, APIKeyAuthMixin)
        assert issubclass(NoteAPI, SimpleAPI)

    def test_api_instance_creation(self):
        """Test that NoteAPI can be instantiated."""
        api_instance = create_api_instance("GET")
        assert api_instance is not None
        assert hasattr(api_instance, "index")
        assert hasattr(api_instance, "create")
        assert hasattr(api_instance, "read")


class TestIndexEndpoint:
    """Tests for the index() method."""

    def test_index_default_parameters(self, mock_request, mock_note):
        """Test index with default parameters."""
        api_instance = create_api_instance("GET")
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            # When sliced, return a mock that has count() method
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_queryset.__getitem__.return_value = mock_sliced
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            result = api_instance.index()

            assert len(result) == 1
            # JSONResponse is a real object, access its attributes
            response = result[0]
            assert response.content is not None

    def test_index_with_limit_parameter(self, mock_request):
        """Test index respects limit parameter."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"limit": "5"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_queryset.__getitem__.return_value = mock_sliced
            mock_queryset.count.return_value = 0
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            # Verify slice with limit=5, offset=0
            mock_queryset.__getitem__.assert_called_with(slice(0, 5))

    def test_index_enforces_max_limit(self, mock_request):
        """Test index enforces maximum limit of 100."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"limit": "200"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_queryset.__getitem__.return_value = mock_sliced
            mock_queryset.count.return_value = 0
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            # Verify max limit=100 is enforced
            mock_queryset.__getitem__.assert_called_with(slice(0, 100))

    def test_index_enforces_min_limit(self, mock_request):
        """Test index enforces minimum limit of 1."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"limit": "-5"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_queryset.__getitem__.return_value = mock_sliced
            mock_queryset.count.return_value = 0
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            # Verify min limit=1 is enforced
            mock_queryset.__getitem__.assert_called_with(slice(0, 1))

    def test_index_with_offset_parameter(self, mock_request):
        """Test index respects offset parameter."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"offset": "10", "limit": "5"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_queryset.__getitem__.return_value = mock_sliced
            mock_queryset.count.return_value = 0
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            # Verify offset=10 and limit=5
            mock_queryset.__getitem__.assert_called_with(slice(10, 15))

    def test_index_negative_offset_defaults_to_zero(self, mock_request):
        """Test index treats negative offset as 0."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"offset": "-5", "limit": "10"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_queryset.__getitem__.return_value = mock_sliced
            mock_queryset.count.return_value = 0
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            # Verify offset=0
            mock_queryset.__getitem__.assert_called_with(slice(0, 10))

    def test_index_filters_by_patient_id(self, mock_request):
        """Test index filters by patient_id."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"patient_id": "patient-123"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(patient__id="patient-123")

    def test_index_filters_by_note_type_code_only(self, mock_request):
        """Test index filters by note_type code only."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"note_type": "progress"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(note_type_version__code="progress")

    def test_index_filters_by_note_type_system_and_code(self, mock_request):
        """Test index filters by note_type system and code."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"note_type": "http://snomed.info/sct|308335008"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(
                note_type_version__system="http://snomed.info/sct",
                note_type_version__code="308335008",
            )

    def test_index_filters_by_datetime_exact(self, mock_request):
        """Test index filters by exact datetime_of_service."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"datetime_of_service": "2025-01-15"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(datetime_of_service="2025-01-15")

    def test_index_filters_by_datetime_gt(self, mock_request):
        """Test index filters by datetime_of_service__gt."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"datetime_of_service__gt": "2025-01-01"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(datetime_of_service__gt="2025-01-01")

    def test_index_filters_by_datetime_gte(self, mock_request):
        """Test index filters by datetime_of_service__gte."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"datetime_of_service__gte": "2025-01-01"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(datetime_of_service__gte="2025-01-01")

    def test_index_filters_by_datetime_lt(self, mock_request):
        """Test index filters by datetime_of_service__lt."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"datetime_of_service__lt": "2025-02-01"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(datetime_of_service__lt="2025-02-01")

    def test_index_filters_by_datetime_lte(self, mock_request):
        """Test index filters by datetime_of_service__lte."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"datetime_of_service__lte": "2025-02-01"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            mock_filtered = MagicMock()
            mock_sliced = MagicMock()
            mock_sliced.count.return_value = 0
            mock_filtered.__getitem__.return_value = mock_sliced
            mock_filtered.count.return_value = 0
            mock_queryset.filter.return_value = mock_filtered
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            api_instance.index()

            mock_queryset.filter.assert_called_with(datetime_of_service__lte="2025-02-01")

    def test_index_next_page_link_when_more_results(self, mock_request):
        """Test next_page link is generated when more results exist."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {"offset": "0", "limit": "10"}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            # First call returns data, second call (for checking next page) returns count > 0
            mock_queryset.__getitem__.side_effect = lambda s: (
                [] if s == slice(0, 10) else MagicMock(count=MagicMock(return_value=5))
            )
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            result = api_instance.index()

            # Result should have JSONResponse
            assert len(result) == 1
            # Verify the link_to_next check was made
            mock_queryset.__getitem__.assert_any_call(slice(10, None))

    def test_index_no_next_page_link_when_no_more_results(self, mock_request):
        """Test next_page is None when no more results exist."""
        api_instance = create_api_instance("GET")
        mock_request.query_params = {}
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.Note.objects") as mock_objects:
            mock_queryset = MagicMock()
            # Return empty for both the main query and the next page check
            mock_queryset.__getitem__.side_effect = lambda s: (
                [] if s == slice(0, 10) else MagicMock(count=MagicMock(return_value=0))
            )
            mock_objects.select_related.return_value.order_by.return_value = mock_queryset

            result = api_instance.index()

            assert len(result) == 1


class TestCreateEndpoint:
    """Tests for the create() method."""

    def test_create_missing_required_fields(self, mock_request):
        """Test create returns 422 when required fields are missing."""
        api_instance = create_api_instance("POST")
        mock_request.json.return_value = {"title": "Test"}
        api_instance.request = mock_request

        result = api_instance.create()

        assert len(result) == 1
        # JSONResponse is real, parse its content
        response = result[0]
        content = json.loads(response.content.decode())
        assert "Missing required attribute(s)" in content["error"]
        assert response.status_code == 422

    def test_create_missing_multiple_fields(self, mock_request):
        """Test create identifies all missing required fields."""
        api_instance = create_api_instance("POST")
        mock_request.json.return_value = {
            "note_type_id": "type-123",
            "title": "Test",
        }
        api_instance.request = mock_request

        result = api_instance.create()

        assert len(result) == 1
        response = result[0]
        content = json.loads(response.content.decode())
        assert "Missing required attribute(s)" in content["error"]
        # Should mention the missing fields
        assert "datetime_of_service" in content["error"]
        assert "patient_id" in content["error"]
        assert "practice_location_id" in content["error"]
        assert "provider_id" in content["error"]

    def test_create_with_all_required_fields(self, mock_request):
        """Test create successfully creates note with all required fields."""
        api_instance = create_api_instance("POST")
        mock_request.json.return_value = {
            "note_type_id": "type-123",
            "datetime_of_service": "2025-02-21 23:31:42",
            "patient_id": "patient-123",
            "practice_location_id": "location-123",
            "provider_id": "provider-123",
            "title": "Test Note",
        }
        api_instance.request = mock_request

        with patch("charting_api_examples.routes.notes.NoteEffect") as mock_effect:
            with patch("charting_api_examples.routes.notes.arrow.get") as mock_arrow:
                mock_datetime = MagicMock()
                mock_arrow.return_value.datetime = mock_datetime

                mock_effect_instance = MagicMock()
                mock_created = MagicMock()
                mock_effect_instance.create.return_value = mock_created
                mock_effect.return_value = mock_effect_instance

                result = api_instance.create()

                # Verify NoteEffect was created with correct parameters
                mock_effect.assert_called_once()
                call_kwargs = mock_effect.call_args[1]
                assert call_kwargs["note_type_id"] == "type-123"
                assert call_kwargs["datetime_of_service"] == mock_datetime
                assert call_kwargs["patient_id"] == "patient-123"
                assert call_kwargs["practice_location_id"] == "location-123"
                assert call_kwargs["provider_id"] == "provider-123"
                assert call_kwargs["title"] == "Test Note"

                # Verify arrow was called to parse datetime
                mock_arrow.assert_called_once_with("2025-02-21 23:31:42")

                # Verify response
                assert len(result) == 2
                assert result[0] == mock_created
                response = result[1]
                content = json.loads(response.content.decode())
                assert content["message"] == "Note data accepted for creation"
                assert response.status_code == HTTPStatus.ACCEPTED


class TestReadEndpoint:
    """Tests for the read() method."""

    def test_read_with_invalid_note_id(self, mock_request):
        """Test read returns 404 for invalid note ID."""
        api_instance = create_api_instance("GET")
        mock_request.path_params = {"id": "invalid-uuid"}
        api_instance.request = mock_request

        with patch(
            "charting_api_examples.routes.notes.get_note_from_path_params"
        ) as mock_get_note:
            mock_get_note.return_value = None

            result = api_instance.read()

            # Result should be the not found response
            response_body = json.loads(result.content.decode())
            assert response_body["error"] == "Note not found."
            assert result.status_code == HTTPStatus.NOT_FOUND

    def test_read_with_valid_note_id(self, mock_request, mock_note):
        """Test read returns note data for valid note ID."""
        api_instance = create_api_instance("GET")
        mock_request.path_params = {"id": "note-123"}
        api_instance.request = mock_request

        with patch(
            "charting_api_examples.routes.notes.get_note_from_path_params"
        ) as mock_get_note:
            mock_get_note.return_value = mock_note

            with patch(
                "charting_api_examples.routes.notes.CurrentNoteStateEvent.objects.get"
            ) as mock_get_state:
                mock_state_event = MagicMock()
                mock_state_event.state = "LOCKED"
                mock_get_state.return_value = mock_state_event

                result = api_instance.read()

                # Verify get_note_from_path_params was called
                mock_get_note.assert_called_once_with({"id": "note-123"})

                # Verify CurrentNoteStateEvent was queried
                mock_get_state.assert_called_once_with(note=mock_note)

                # Verify response
                assert len(result) == 1
                response = result[0]
                content = json.loads(response.content.decode())
                assert content["note"]["id"] == "note-123"
                assert content["note"]["patient_id"] == "patient-123"
                assert content["note"]["provider_id"] == "provider-123"
                assert content["note"]["state"] == "LOCKED"
                assert content["note"]["note_type"]["name"] == "Progress Note"
                assert response.status_code == HTTPStatus.OK
