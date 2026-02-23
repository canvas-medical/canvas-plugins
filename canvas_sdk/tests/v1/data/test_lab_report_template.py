import pytest

from canvas_sdk.test_utils.factories import (
    LabReportTemplateFactory,
    LabReportTemplateFieldFactory,
    LabReportTemplateFieldOptionFactory,
)
from canvas_sdk.v1.data import (
    LabReportTemplate,
    LabReportTemplateField,
)
from canvas_sdk.v1.data.lab import FieldType


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
        type=FieldType.FLOAT,
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
        type=FieldType.SELECT,
        sequence=1,
    )
    LabReportTemplateFieldOptionFactory.create(field=select_field, label="Positive", key="pos")
    LabReportTemplateFieldOptionFactory.create(field=select_field, label="Negative", key="neg")

    # Inactive template
    LabReportTemplateFactory.create(name="Deprecated Test", active=False)


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


def test_all_types_defined() -> None:
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


def test_type_values_match_source() -> None:
    """Test field type values match ParseTemplates constants."""
    assert FieldType.FLOAT.value == "float"
    assert FieldType.SELECT.value == "select"
    assert FieldType.LAB_REPORT.value == "labReport"
    assert FieldType.REMOTE_FIELDS.value == "remoteFields"


@pytest.mark.django_db
def test_type_attribute() -> None:
    """Test type maps to type column correctly."""
    field = LabReportTemplateField.objects.get(label="Result")
    assert field.type == FieldType.SELECT
