from unittest.mock import Mock

from canvas_sdk.v1.data.specialty_report_template import (
    SpecialtyReportTemplate,
    SpecialtyReportTemplateField,
    SpecialtyReportTemplateFieldOption,
    SpecialtyReportTemplateQuerySet,
)


def test_active_filters_by_active_true() -> None:
    """Test that active() filters for active=True."""
    mock_qs = Mock(spec=SpecialtyReportTemplateQuerySet)
    SpecialtyReportTemplateQuerySet.active(mock_qs)
    mock_qs.filter.assert_called_once_with(active=True)


def test_search_filters_by_keywords() -> None:
    """Test that search() filters by search_keywords."""
    mock_qs = Mock(spec=SpecialtyReportTemplateQuerySet)
    SpecialtyReportTemplateQuerySet.search(mock_qs, "cardiology")
    mock_qs.filter.assert_called_once_with(search_keywords__icontains="cardiology")


def test_custom_filters_by_custom_true() -> None:
    """Test that custom() filters for custom=True."""
    mock_qs = Mock(spec=SpecialtyReportTemplateQuerySet)
    SpecialtyReportTemplateQuerySet.custom(mock_qs)
    mock_qs.filter.assert_called_once_with(custom=True)


def test_builtin_filters_by_custom_false() -> None:
    """Test that builtin() filters for custom=False."""
    mock_qs = Mock(spec=SpecialtyReportTemplateQuerySet)
    SpecialtyReportTemplateQuerySet.builtin(mock_qs)
    mock_qs.filter.assert_called_once_with(custom=False)


def test_by_specialty_filters_by_specialty_code() -> None:
    """Test that by_specialty() filters by specialty_code."""
    mock_qs = Mock(spec=SpecialtyReportTemplateQuerySet)
    SpecialtyReportTemplateQuerySet.by_specialty(mock_qs, "207RC0000X")
    mock_qs.filter.assert_called_once_with(specialty_code="207RC0000X")


def test_relationships() -> None:
    """Test that model relationships are set up correctly."""
    field_relation = SpecialtyReportTemplate._meta.get_field("fields")
    assert field_relation.related_model == SpecialtyReportTemplateField

    option_relation = SpecialtyReportTemplateField._meta.get_field("options")
    assert option_relation.related_model == SpecialtyReportTemplateFieldOption

    template_relation = SpecialtyReportTemplateField._meta.get_field("report_template")
    assert template_relation.related_model == SpecialtyReportTemplate
