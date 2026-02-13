import pytest

from canvas_sdk.test_utils.factories import (
    LabReportTemplateFactory,
    LabReportTemplateFieldFactory,
    LabReportTemplateFieldOptionFactory,
)
from canvas_sdk.v1.data import (
    LabReportTemplate,
    LabReportTemplateField,
    LabReportTemplateFieldOption,
)
from canvas_sdk.v1.data.lab_report_template import FieldType


@pytest.fixture(autouse=True)
def setup_templates(db: None) -> None:
    """Set up test data for all tests."""
    # Active POC template
    poc_template = LabReportTemplateFactory.create(
        name="Glucose POC",
        active=True,
        poc=True,
        custom=False,
        search_keywords="glucose blood sugar",
    )
    LabReportTemplateFieldFactory.create(
        report_template=poc_template,
        label="Glucose Level",
        field_type=FieldType.FLOAT,
        sequence=1,
    )

    # Active custom template with select field
    custom_template = LabReportTemplateFactory.create(
        name="Custom Lab Panel",
        active=True,
        poc=False,
        custom=True,
        search_keywords="panel custom",
    )
    select_field = LabReportTemplateFieldFactory.create(
        report_template=custom_template,
        label="Result",
        field_type=FieldType.SELECT,
        sequence=1,
    )
    LabReportTemplateFieldOptionFactory.create(field=select_field, label="Positive", key="pos")
    LabReportTemplateFieldOptionFactory.create(field=select_field, label="Negative", key="neg")

    # Inactive template
    LabReportTemplateFactory.create(name="Deprecated Test", active=False)


@pytest.mark.django_db
def test_active_returns_only_active_templates() -> None:
    """Test active() filters for active=True."""
    result = LabReportTemplate.objects.active()
    assert result.count() == 2
    assert all(t.active for t in result)


@pytest.mark.django_db
def test_inactive_returns_only_inactive_templates() -> None:
    """Test inactive() filters for active=False."""
    result = LabReportTemplate.objects.inactive()
    assert result.count() == 1
    first_template = result.first()
    assert first_template is not None
    assert not first_template.active


@pytest.mark.django_db
def test_search_by_name() -> None:
    """Test search() matches template name."""
    result = LabReportTemplate.objects.search("Glucose")
    assert result.count() == 1
    first_template = result.first()
    assert first_template is not None
    assert first_template.name == "Glucose POC"


@pytest.mark.django_db
def test_search_by_keywords() -> None:
    """Test search() matches search_keywords."""
    result = LabReportTemplate.objects.search("panel")
    assert result.count() == 1
    first_template = result.first()
    assert first_template is not None
    assert first_template.name == "Custom Lab Panel"


@pytest.mark.django_db
def test_search_empty_returns_all() -> None:
    """Test search() with empty string returns unchanged queryset."""
    result = LabReportTemplate.objects.search("")
    assert result.count() == 3


@pytest.mark.django_db
def test_point_of_care_returns_poc_templates() -> None:
    """Test point_of_care() filters for poc=True."""
    result = LabReportTemplate.objects.point_of_care()
    assert result.count() == 1
    first_template = result.first()
    assert first_template is not None
    assert first_template.poc is True


@pytest.mark.django_db
def test_custom_returns_custom_templates() -> None:
    """Test custom() filters for custom=True."""
    result = LabReportTemplate.objects.custom()
    assert all(t.custom for t in result)


@pytest.mark.django_db
def test_builtin_returns_builtin_templates() -> None:
    """Test builtin() filters for custom=False."""
    result = LabReportTemplate.objects.builtin()
    assert result.count() == 1
    first_template = result.first()
    assert first_template is not None
    assert first_template.custom is False


@pytest.mark.django_db
def test_method_chaining() -> None:
    """Test QuerySet methods can be chained."""
    result = LabReportTemplate.objects.active().point_of_care()
    assert result.count() == 1
    first_template = result.first()
    assert first_template is not None
    assert first_template.name == "Glucose POC"


@pytest.mark.django_db
def test_prefetch_fields() -> None:
    """Test prefetch_related('fields') works."""
    template = LabReportTemplate.objects.prefetch_related("fields").get(name="Custom Lab Panel")
    # Access fields without additional query
    assert template.fields.count() == 1


@pytest.mark.django_db
def test_prefetch_fields_and_options() -> None:
    """Test prefetch_related('fields', 'fields__options') works."""
    template = LabReportTemplate.objects.prefetch_related("fields", "fields__options").get(
        name="Custom Lab Panel"
    )

    # Access nested options without additional queries
    field = template.fields.first()
    assert field.options.count() == 2


def test_all_field_types_defined() -> None:
    """Test all 10 field types are defined."""
    expected_types = {
        "FLOAT",
        "SELECT",
        "TEXT",
        "CHECKBOX",
        "RADIO",
        "ARRAY",
        "LAB_REPORT",
        "REMOTE_FIELDS",
        "AUTOCOMPLETE",
        "DATE",
    }
    actual_types = {choice.name for choice in FieldType}
    assert actual_types == expected_types


def test_field_type_values_match_source() -> None:
    """Test field type values match ParseTemplates constants."""
    assert FieldType.FLOAT.value == "float"
    assert FieldType.SELECT.value == "select"
    assert FieldType.LAB_REPORT.value == "labReport"
    assert FieldType.REMOTE_FIELDS.value == "remoteFields"


@pytest.mark.django_db
def test_template_str_representation() -> None:
    """Test __str__ returns template name."""
    template = LabReportTemplate.objects.get(name="Glucose POC")
    assert str(template) == "Glucose POC"


@pytest.mark.django_db
def test_field_str_representation() -> None:
    """Test __str__ returns field label."""
    field = LabReportTemplateField.objects.get(label="Glucose Level")
    assert str(field) == "Glucose Level"


@pytest.mark.django_db
def test_field_type_attribute() -> None:
    """Test field_type maps to type column correctly."""
    field = LabReportTemplateField.objects.get(label="Result")
    assert field.field_type == FieldType.SELECT


@pytest.mark.django_db
def test_option_str_representation() -> None:
    """Test __str__ returns label and key."""
    option = LabReportTemplateFieldOption.objects.get(key="pos")
    assert str(option) == "Positive (pos)"


@pytest.mark.django_db
def test_lab_report_template_queryset_point_of_care() -> None:
    """Test LabReportTemplateQuerySet.point_of_care() filters POC templates."""
    poc_template = LabReportTemplateFactory.create(poc=True)
    regular_template = LabReportTemplateFactory.create(poc=False)

    result = LabReportTemplate.objects.point_of_care()

    assert poc_template in result
    assert regular_template not in result
