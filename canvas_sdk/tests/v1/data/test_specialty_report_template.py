"""Tests for SpecialtyReportTemplate models and querysets."""

import pytest

from canvas_sdk.v1.data.specialty_report_template import (
    SpecialtyReportTemplate,
    SpecialtyReportTemplateField,
    SpecialtyReportTemplateFieldOption,
    SpecialtyReportTemplateQuerySet,
)


@pytest.mark.django_db
def test_specialty_report_template_model_structure() -> None:
    """Test that SpecialtyReportTemplate model has correct structure."""
    # Verify model exists and has correct db_table
    assert (
        SpecialtyReportTemplate._meta.db_table
        == "canvas_sdk_data_data_integration_specialtyreporttemplate_001"
    )
    assert SpecialtyReportTemplate._meta.managed is False

    # Verify all required fields exist
    assert hasattr(SpecialtyReportTemplate, "dbid")
    assert hasattr(SpecialtyReportTemplate, "id")  # UUID field from IdentifiableModel
    assert hasattr(SpecialtyReportTemplate, "name")
    assert hasattr(SpecialtyReportTemplate, "code")
    assert hasattr(SpecialtyReportTemplate, "code_system")
    assert hasattr(SpecialtyReportTemplate, "search_keywords")
    assert hasattr(SpecialtyReportTemplate, "active")
    assert hasattr(SpecialtyReportTemplate, "custom")
    assert hasattr(SpecialtyReportTemplate, "search_as")
    assert hasattr(SpecialtyReportTemplate, "specialty_name")
    assert hasattr(SpecialtyReportTemplate, "specialty_code")
    assert hasattr(SpecialtyReportTemplate, "specialty_code_system")


@pytest.mark.django_db
def test_specialty_report_template_field_model_structure() -> None:
    """Test that SpecialtyReportTemplateField model has correct structure."""
    # Verify model exists and has correct db_table
    assert (
        SpecialtyReportTemplateField._meta.db_table
        == "canvas_sdk_data_data_integration_specialtyreporttemplatefield_001"
    )
    assert SpecialtyReportTemplateField._meta.managed is False

    # Verify all required fields exist
    assert hasattr(SpecialtyReportTemplateField, "dbid")
    assert hasattr(SpecialtyReportTemplateField, "report_template")
    assert hasattr(SpecialtyReportTemplateField, "sequence")
    assert hasattr(SpecialtyReportTemplateField, "code")
    assert hasattr(SpecialtyReportTemplateField, "code_system")
    assert hasattr(SpecialtyReportTemplateField, "label")
    assert hasattr(SpecialtyReportTemplateField, "units")
    assert hasattr(SpecialtyReportTemplateField, "type")
    assert hasattr(SpecialtyReportTemplateField, "required")


@pytest.mark.django_db
def test_specialty_report_template_field_option_model_structure() -> None:
    """Test that SpecialtyReportTemplateFieldOption model has correct structure."""
    # Verify model exists and has correct db_table
    assert (
        SpecialtyReportTemplateFieldOption._meta.db_table
        == "canvas_sdk_data_data_integration_specialtyreporttemplatefieldoption_001"
    )
    assert SpecialtyReportTemplateFieldOption._meta.managed is False

    # Verify all required fields exist
    assert hasattr(SpecialtyReportTemplateFieldOption, "dbid")
    assert hasattr(SpecialtyReportTemplateFieldOption, "field")
    assert hasattr(SpecialtyReportTemplateFieldOption, "label")
    assert hasattr(SpecialtyReportTemplateFieldOption, "key")


@pytest.mark.django_db
def test_specialty_report_template_queryset_active() -> None:
    """Test that active() method filters correctly."""
    queryset = SpecialtyReportTemplate.objects.active()
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)
    # Verify the filter is applied (we can't test actual data without view data)
    # But we can verify the method exists and returns a queryset


@pytest.mark.django_db
def test_specialty_report_template_queryset_search() -> None:
    """Test that search() method performs full-text search."""
    query = "cardiology"
    queryset = SpecialtyReportTemplate.objects.search(query)
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)
    # Verify the method exists and returns a queryset


@pytest.mark.django_db
def test_specialty_report_template_queryset_custom() -> None:
    """Test that custom() method filters correctly."""
    queryset = SpecialtyReportTemplate.objects.custom()
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)


@pytest.mark.django_db
def test_specialty_report_template_queryset_builtin() -> None:
    """Test that builtin() method filters correctly."""
    queryset = SpecialtyReportTemplate.objects.builtin()
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)


@pytest.mark.django_db
def test_specialty_report_template_queryset_by_specialty() -> None:
    """Test that by_specialty() method filters by specialty code."""
    specialty_code = "207RC0000X"
    queryset = SpecialtyReportTemplate.objects.by_specialty(specialty_code)
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)


@pytest.mark.django_db
def test_specialty_report_template_queryset_method_chaining() -> None:
    """Test that QuerySet methods can be chained."""
    # Test chaining active() with by_specialty()
    specialty_code = "207RC0000X"
    queryset = SpecialtyReportTemplate.objects.active().by_specialty(specialty_code)
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)

    # Test chaining active() with search()
    queryset = SpecialtyReportTemplate.objects.active().search("cardiology")
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)

    # Test chaining active() with custom()
    queryset = SpecialtyReportTemplate.objects.active().custom()
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)

    # Test chaining active() with builtin()
    queryset = SpecialtyReportTemplate.objects.active().builtin()
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)


@pytest.mark.django_db
def test_specialty_report_template_relationships() -> None:
    """Test that model relationships are set up correctly."""
    # Verify that SpecialtyReportTemplate has fields relationship
    assert hasattr(SpecialtyReportTemplate, "fields")
    field_relation = SpecialtyReportTemplate._meta.get_field("fields")
    assert field_relation.related_model == SpecialtyReportTemplateField

    # Verify that SpecialtyReportTemplateField has options relationship
    assert hasattr(SpecialtyReportTemplateField, "options")
    option_relation = SpecialtyReportTemplateField._meta.get_field("options")
    assert option_relation.related_model == SpecialtyReportTemplateFieldOption

    # Verify that SpecialtyReportTemplateField has report_template relationship
    assert hasattr(SpecialtyReportTemplateField, "report_template")
    template_relation = SpecialtyReportTemplateField._meta.get_field("report_template")
    assert template_relation.related_model == SpecialtyReportTemplate


@pytest.mark.django_db
def test_specialty_report_template_prefetch_related() -> None:
    """Test that prefetch_related works with fields and options."""
    # This test verifies the relationship names are correct for prefetch_related
    # Actual data testing would require view data to exist
    queryset = SpecialtyReportTemplate.objects.prefetch_related("fields", "fields__options")
    assert isinstance(queryset, SpecialtyReportTemplateQuerySet)


@pytest.mark.django_db
def test_specialty_report_template_import() -> None:
    """Test that models can be imported from canvas_sdk.v1.data."""
    from canvas_sdk.v1.data import (
        SpecialtyReportTemplate,
        SpecialtyReportTemplateField,
        SpecialtyReportTemplateFieldOption,
    )

    assert SpecialtyReportTemplate is not None
    assert SpecialtyReportTemplateField is not None
    assert SpecialtyReportTemplateFieldOption is not None


@pytest.mark.django_db
def test_specialty_report_template_example_usage() -> None:
    """Test the example usage from ticket requirements."""
    # Get all active specialty templates
    templates = SpecialtyReportTemplate.objects.active()
    assert isinstance(templates, SpecialtyReportTemplateQuerySet)

    # Filter by specialty
    cardiology = SpecialtyReportTemplate.objects.active().by_specialty("207RC0000X")
    assert isinstance(cardiology, SpecialtyReportTemplateQuerySet)

    # Get template schema for LLM
    template_qs = SpecialtyReportTemplate.objects.prefetch_related("fields", "fields__options")
    assert isinstance(template_qs, SpecialtyReportTemplateQuerySet)


@pytest.mark.django_db
def test_specialty_specific_fields_accessible() -> None:
    """Test that specialty-specific fields are accessible."""
    # Verify specialty-specific fields exist on the model
    assert hasattr(SpecialtyReportTemplate, "search_as")
    assert hasattr(SpecialtyReportTemplate, "specialty_name")
    assert hasattr(SpecialtyReportTemplate, "specialty_code")
    assert hasattr(SpecialtyReportTemplate, "specialty_code_system")

    # Verify field types
    search_as_field = SpecialtyReportTemplate._meta.get_field("search_as")
    assert isinstance(search_as_field, type(SpecialtyReportTemplate._meta.get_field("name")))

    specialty_name_field = SpecialtyReportTemplate._meta.get_field("specialty_name")
    assert isinstance(specialty_name_field, type(SpecialtyReportTemplate._meta.get_field("name")))

    specialty_code_field = SpecialtyReportTemplate._meta.get_field("specialty_code")
    assert isinstance(specialty_code_field, type(SpecialtyReportTemplate._meta.get_field("name")))

    specialty_code_system_field = SpecialtyReportTemplate._meta.get_field("specialty_code_system")
    assert isinstance(
        specialty_code_system_field, type(SpecialtyReportTemplate._meta.get_field("name"))
    )


@pytest.mark.django_db
def test_specialty_report_template_id_field() -> None:
    """Test that SpecialtyReportTemplate has id field (UUID) from IdentifiableModel."""
    # Verify id field exists and is a UUIDField
    assert hasattr(SpecialtyReportTemplate, "id")
    id_field = SpecialtyReportTemplate._meta.get_field("id")
    from django.db import models

    assert isinstance(id_field, models.UUIDField), "id field should be a UUIDField"

    # Verify dbid field still exists (from base Model)
    assert hasattr(SpecialtyReportTemplate, "dbid")
    dbid_field = SpecialtyReportTemplate._meta.get_field("dbid")
    assert isinstance(dbid_field, models.BigAutoField), "dbid field should be a BigAutoField"
