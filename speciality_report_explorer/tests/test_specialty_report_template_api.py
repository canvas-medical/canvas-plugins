"""Tests for speciality_report_explorer plugin.

This module contains comprehensive unit tests for the SpecialtyReportTemplateAPI
Simple API endpoint. Tests verify query parameter handling, filtering, and response
formatting using mocked SDK models.
"""

import json
from typing import Any
from unittest.mock import Mock, patch

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.v1.data import SpecialtyReportTemplate
from speciality_report_explorer.protocols.specialty_report_template_api import (
    SpecialtyReportTemplateAPI,
)


# Test Fixtures and Helpers
class DummyRequest:
    """A dummy request object for testing SpecialtyReportTemplateAPI.

    Mimics the request object structure used by SimpleAPIRoute handlers,
    providing path, path_params, and query_params attributes.
    """

    def __init__(
        self,
        path: str = "/specialty-report-templates",
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, str] | None = None,
    ) -> None:
        """Initialize dummy request with path and parameters.

        Args:
            path: Request path (default: "/specialty-report-templates")
            path_params: Path parameters dictionary (default: empty dict)
            query_params: Query parameters dictionary (default: empty dict)
        """
        self.path = path
        self.path_params = path_params or {}
        self.query_params = query_params or {}


class DummyEvent:
    """A dummy event object for testing API handlers.

    Mimics the event structure used by SimpleAPIRoute handlers,
    providing context and target attributes.
    """

    def __init__(self, context: dict[str, Any] | None = None, target: str | None = None) -> None:
        """Initialize dummy event with context and target.

        Args:
            context: Event context dictionary (default: empty dict)
            target: Event target identifier (default: None)
        """
        self.context = context or {}
        self.target = target


def create_mock_template(
    dbid: int = 1,
    name: str = "Test Template",
    code: str = "TEST001",
    code_system: str = "http://example.com/codes",
    search_keywords: str = "test",
    active: bool = True,
    custom: bool = False,
    search_as: str = "test",
    specialty_name: str = "Test Specialty",
    specialty_code: str = "207RC0000X",
    specialty_code_system: str = "http://nucc.org/provider-taxonomy",
    fields: list[Mock] | None = None,
) -> Mock:
    """Create a mock SpecialtyReportTemplate instance.

    Args:
        dbid: Template database ID (default: 1)
        name: Template name (default: "Test Template")
        code: Template code (default: "TEST001")
        code_system: Code system URI (default: "http://example.com/codes")
        search_keywords: Search keywords (default: "test")
        active: Active status (default: True)
        custom: Custom flag (default: False)
        search_as: Search as value (default: "test")
        specialty_name: Specialty name (default: "Test Specialty")
        specialty_code: Specialty code (default: "207RC0000X")
        specialty_code_system: Specialty code system URI (default: "http://nucc.org/provider-taxonomy")
        fields: List of mock field objects (default: None, creates empty list)

    Returns:
        Mock: Configured mock SpecialtyReportTemplate instance
    """
    mock_template = Mock(spec=SpecialtyReportTemplate)
    mock_template.dbid = dbid
    mock_template.name = name
    mock_template.code = code
    mock_template.code_system = code_system
    mock_template.search_keywords = search_keywords
    mock_template.active = active
    mock_template.custom = custom
    mock_template.search_as = search_as
    mock_template.specialty_name = specialty_name
    mock_template.specialty_code = specialty_code
    mock_template.specialty_code_system = specialty_code_system

    fields_list = fields or []
    mock_template.fields.all.return_value = fields_list
    # Note: fields.count() is not used in the API, but kept for compatibility
    mock_template.fields.count.return_value = len(fields_list)

    return mock_template


def create_mock_field(
    dbid: int = 1,
    sequence: int = 1,
    code: str | None = "TEST_FIELD",
    code_system: str = "http://loinc.org",
    label: str = "Test Field",
    units: str | None = None,
    type: str = "text",  # noqa: A002
    required: bool = True,
    options: list[Mock] | None = None,
) -> Mock:
    """Create a mock SpecialtyReportTemplateField instance.

    Args:
        dbid: Field database ID (default: 1)
        sequence: Field sequence number (default: 1)
        code: Field code (default: "TEST_FIELD")
        code_system: Code system URI (default: "http://loinc.org")
        label: Field label (default: "Test Field")
        units: Field units (default: None)
        type: Field type (default: "text")
        required: Required flag (default: True)
        options: List of mock option objects (default: None, creates empty list)

    Returns:
        Mock: Configured mock SpecialtyReportTemplateField instance
    """
    mock_field = Mock()
    mock_field.dbid = dbid
    mock_field.sequence = sequence
    mock_field.code = code
    mock_field.code_system = code_system
    mock_field.label = label
    mock_field.units = units
    mock_field.type = type
    mock_field.required = required

    options_list = options or []
    mock_field.options.all.return_value = options_list

    return mock_field


def create_mock_option(dbid: int = 1, label: str = "Option 1", key: str = "OPTION1") -> Mock:
    """Create a mock SpecialtyReportTemplateFieldOption instance.

    Args:
        dbid: Option database ID (default: 1)
        label: Option label (default: "Option 1")
        key: Option key (default: "OPTION1")

    Returns:
        Mock: Configured mock SpecialtyReportTemplateFieldOption instance
    """
    mock_option = Mock()
    mock_option.dbid = dbid
    mock_option.label = label
    mock_option.key = key
    return mock_option


def create_mock_queryset(templates: list[Mock]) -> Mock:
    """Create a mock QuerySet that returns the given templates.

    Args:
        templates: List of mock template objects to return

    Returns:
        Mock: Configured mock QuerySet that supports chaining and iteration
    """
    mock_queryset = Mock()
    mock_queryset.all.return_value = mock_queryset
    mock_queryset.active.return_value = mock_queryset
    mock_queryset.search.return_value = mock_queryset
    mock_queryset.custom.return_value = mock_queryset
    mock_queryset.builtin.return_value = mock_queryset
    mock_queryset.by_specialty.return_value = mock_queryset
    mock_queryset.prefetch_related.return_value = mock_queryset
    mock_queryset.__iter__ = lambda self: iter(templates)
    mock_queryset.__getitem__ = (
        lambda self, key: templates[:key] if isinstance(key, int) else templates[key]
    )

    return mock_queryset


def create_api_instance(
    request: DummyRequest, context: dict[str, Any] | None = None
) -> SpecialtyReportTemplateAPI:
    """Create and configure a SpecialtyReportTemplateAPI instance for testing.

    Args:
        request: DummyRequest instance to attach to API
        context: Event context dictionary (default: {"method": "GET", "path": "/specialty-report-templates"})

    Returns:
        SpecialtyReportTemplateAPI: Configured API instance with request attached
    """
    if context is None:
        context = {"method": "GET", "path": "/specialty-report-templates"}

    api = SpecialtyReportTemplateAPI(event=DummyEvent(context=context))  # type: ignore[arg-type]
    api.request = request
    return api


# Test Cases
def test_import_specialty_report_template_api() -> None:
    """Test that SpecialtyReportTemplateAPI can be imported without errors."""
    assert SpecialtyReportTemplateAPI is not None
    assert hasattr(SpecialtyReportTemplateAPI, "PATH")
    assert hasattr(SpecialtyReportTemplateAPI, "get")
    assert hasattr(SpecialtyReportTemplateAPI, "authenticate")


def test_specialty_report_template_api_path_configuration() -> None:
    """Test that SpecialtyReportTemplateAPI has correct path configuration."""
    expected_path = "/specialty-report-templates"
    assert expected_path == SpecialtyReportTemplateAPI.PATH, (
        f"Expected PATH to be '{expected_path}', got '{SpecialtyReportTemplateAPI.PATH}'"
    )


class TestSpecialtyReportTemplateAPI:
    """Test suite for SpecialtyReportTemplateAPI endpoint.

    Tests cover authentication, query parameter parsing, filtering, and response formatting.
    All tests use mocked SDK models to isolate API handler logic.
    """

    def test_authenticate_returns_true(self) -> None:
        """Test authentication always succeeds for testing purposes."""
        request = DummyRequest()
        api = create_api_instance(request)

        mock_credentials = Mock()
        result = api.authenticate(mock_credentials)

        assert result is True, "Authentication should always return True for testing"

    def test_get_returns_template_list(self) -> None:
        """Test GET endpoint returns list of templates in correct format."""
        # Arrange
        mock_template = create_mock_template()
        mock_queryset = create_mock_queryset([mock_template])
        request = DummyRequest()
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            result = api.get()

        # Assert
        assert len(result) == 1, "Should return exactly one JSONResponse"
        assert isinstance(result[0], JSONResponse), "Result should be a JSONResponse instance"

        # Verify response payload structure
        payload = json.loads(result[0].content.decode())
        assert "count" in payload, "Response should include 'count' field"
        assert "templates" in payload, "Response should include 'templates' field"
        assert payload["count"] == 1, "Count should match number of templates"
        assert len(payload["templates"]) == 1, "Templates array should contain one template"

        # Verify template structure
        template_data = payload["templates"][0]
        assert template_data["dbid"] == 1, "Template dbid should be 1"
        assert template_data["name"] == "Test Template", "Template name should match"
        assert "fields" not in template_data, "Fields should not be included by default"

    def test_get_with_active_filter(self) -> None:
        """Test GET endpoint applies active filter correctly."""
        # Arrange
        mock_queryset = create_mock_queryset([])
        request = DummyRequest(query_params={"active": "true"})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            api.get()

        # Assert
        mock_queryset.active.assert_called_once_with()

    def test_get_with_search_filter(self) -> None:
        """Test GET endpoint applies search filter correctly."""
        # Arrange
        search_query = "cardiology"
        mock_queryset = create_mock_queryset([])
        request = DummyRequest(query_params={"search": search_query})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            api.get()

        # Assert
        mock_queryset.search.assert_called_once_with(search_query)

    def test_get_with_custom_filter_true(self) -> None:
        """Test GET endpoint applies custom=true filter correctly."""
        # Arrange
        mock_queryset = create_mock_queryset([])
        request = DummyRequest(query_params={"custom": "true"})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            api.get()

        # Assert
        mock_queryset.custom.assert_called_once_with()
        mock_queryset.builtin.assert_not_called()

    def test_get_with_custom_filter_false(self) -> None:
        """Test GET endpoint applies custom=false filter correctly."""
        # Arrange
        mock_queryset = create_mock_queryset([])
        request = DummyRequest(query_params={"custom": "false"})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            api.get()

        # Assert
        mock_queryset.builtin.assert_called_once_with()
        mock_queryset.custom.assert_not_called()

    def test_get_with_specialty_code_filter(self) -> None:
        """Test GET endpoint applies specialty_code filter correctly."""
        # Arrange
        specialty_code = "207RC0000X"
        mock_queryset = create_mock_queryset([])
        request = DummyRequest(query_params={"specialty_code": specialty_code})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            api.get()

        # Assert
        mock_queryset.by_specialty.assert_called_once_with(specialty_code)

    def test_get_with_include_fields(self) -> None:
        """Test GET endpoint includes fields when include_fields=true."""
        # Arrange
        mock_field = create_mock_field()
        mock_template = create_mock_template(fields=[mock_field])
        mock_queryset = create_mock_queryset([mock_template])
        request = DummyRequest(query_params={"include_fields": "true"})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            result = api.get()

        # Assert
        mock_queryset.prefetch_related.assert_called_once_with("fields", "fields__options")

        assert len(result) == 1, "Should return exactly one JSONResponse"
        assert isinstance(result[0], JSONResponse), "Result should be a JSONResponse instance"

        payload = json.loads(result[0].content.decode())
        template_data = payload["templates"][0]
        assert "fields" in template_data, "Fields should be included when include_fields=true"
        assert "field_count" in template_data, "Field count should be included"
        assert template_data["field_count"] == 1, "Field count should be 1"
        assert len(template_data["fields"]) == 1, "Fields array should contain one field"

        # Verify field structure
        field_data = template_data["fields"][0]
        assert field_data["dbid"] == 1, "Field dbid should be 1"
        assert field_data["sequence"] == 1, "Field sequence should be 1"
        assert field_data["label"] == "Test Field", "Field label should match"
        assert "options" not in field_data, (
            "Options should not be included when include_options=false"
        )

    def test_get_with_include_options(self) -> None:
        """Test GET endpoint includes options when include_options=true."""
        # Arrange
        mock_option = create_mock_option()
        mock_field = create_mock_field(type="select", options=[mock_option])
        mock_template = create_mock_template(fields=[mock_field])
        mock_queryset = create_mock_queryset([mock_template])
        request = DummyRequest(query_params={"include_fields": "true", "include_options": "true"})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            result = api.get()

        # Assert
        assert len(result) == 1, "Should return exactly one JSONResponse"
        assert isinstance(result[0], JSONResponse), "Result should be a JSONResponse instance"

        payload = json.loads(result[0].content.decode())
        template_data = payload["templates"][0]
        assert "fields" in template_data, "Fields should be included when include_fields=true"

        field_data = template_data["fields"][0]
        assert "options" in field_data, "Options should be included when include_options=true"
        assert "option_count" in field_data, "Option count should be included"
        assert field_data["option_count"] == 1, "Option count should be 1"
        assert len(field_data["options"]) == 1, "Options array should contain one option"

        # Verify option structure
        option_data = field_data["options"][0]
        assert option_data["dbid"] == 1, "Option dbid should be 1"
        assert option_data["label"] == "Option 1", "Option label should match"
        assert option_data["key"] == "OPTION1", "Option key should match"

    def test_get_with_multiple_filters(self) -> None:
        """Test GET endpoint applies multiple filters correctly."""
        # Arrange
        mock_queryset = create_mock_queryset([])
        request = DummyRequest(
            query_params={
                "active": "true",
                "search": "cardiology",
                "custom": "false",
                "specialty_code": "207RC0000X",
            }
        )
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            api.get()

        # Assert - verify all filters were applied
        mock_queryset.active.assert_called_once_with()
        mock_queryset.search.assert_called_once_with("cardiology")
        mock_queryset.builtin.assert_called_once_with()
        mock_queryset.by_specialty.assert_called_once_with("207RC0000X")

    def test_get_with_empty_results(self) -> None:
        """Test GET endpoint handles empty results correctly."""
        # Arrange
        mock_queryset = create_mock_queryset([])
        request = DummyRequest()
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            result = api.get()

        # Assert
        assert len(result) == 1, "Should return exactly one JSONResponse"
        payload = json.loads(result[0].content.decode())
        assert payload["count"] == 0, "Count should be 0 for empty results"
        assert payload["templates"] == [], "Templates array should be empty"

    def test_get_with_max_results_limit(self) -> None:
        """Test GET endpoint limits results to MAX_RESULTS (20)."""
        # Arrange - create 25 mock templates
        mock_templates = [create_mock_template(dbid=i, name=f"Template {i}") for i in range(1, 26)]
        mock_queryset = create_mock_queryset(mock_templates)
        request = DummyRequest()
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            result = api.get()

        # Assert
        payload = json.loads(result[0].content.decode())
        assert payload["count"] == 20, "Count should be limited to 20 templates"
        assert len(payload["templates"]) == 20, "Templates array should contain exactly 20 items"

    def test_get_with_fields_sorted_by_sequence(self) -> None:
        """Test GET endpoint sorts fields by sequence when include_fields=true."""
        # Arrange - create fields with non-sequential order
        mock_field_3 = create_mock_field(dbid=3, sequence=3, label="Field 3")
        mock_field_1 = create_mock_field(dbid=1, sequence=1, label="Field 1")
        mock_field_2 = create_mock_field(dbid=2, sequence=2, label="Field 2")
        mock_template = create_mock_template(
            fields=[mock_field_3, mock_field_1, mock_field_2]  # Out of order
        )
        mock_queryset = create_mock_queryset([mock_template])
        request = DummyRequest(query_params={"include_fields": "true"})
        api = create_api_instance(request)

        # Act
        with patch.object(SpecialtyReportTemplate, "objects", mock_queryset):
            result = api.get()

        # Assert - fields should be sorted by sequence
        payload = json.loads(result[0].content.decode())
        fields = payload["templates"][0]["fields"]
        assert len(fields) == 3, "Should have 3 fields"
        assert fields[0]["sequence"] == 1, "First field should have sequence 1"
        assert fields[1]["sequence"] == 2, "Second field should have sequence 2"
        assert fields[2]["sequence"] == 3, "Third field should have sequence 3"
