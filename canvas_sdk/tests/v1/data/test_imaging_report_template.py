from canvas_sdk.v1.data.imaging import (
    ImagingReportTemplate,
    ImagingReportTemplateField,
    ImagingReportTemplateFieldOption,
    ImagingReportTemplateQuerySet,
)


def test_imaging_template_db_table_name() -> None:
    """Ensure the model uses the correct database table."""
    assert (
        ImagingReportTemplate._meta.db_table
        == "canvas_sdk_data_data_integration_imagingreporttemplate_001"
    )


def test_imaging_template_model_fields() -> None:
    """Ensure all expected fields are defined."""
    field_names = {f.name for f in ImagingReportTemplate._meta.get_fields()}
    expected_fields = {
        "dbid",
        "id",
        "name",
        "long_name",
        "code",
        "code_system",
        "search_keywords",
        "active",
        "custom",
        "rank",
        "fields",  # reverse relation
    }
    assert expected_fields.issubset(field_names)


def test_imaging_field_db_table_name() -> None:
    """Ensure the model uses the correct database table."""
    assert (
        ImagingReportTemplateField._meta.db_table
        == "canvas_sdk_data_data_integration_imagingreporttemplatefield_001"
    )


def test_imaging_field_model_fields() -> None:
    """Ensure all expected fields are defined."""
    field_names = {f.name for f in ImagingReportTemplateField._meta.get_fields()}
    expected_fields = {
        "dbid",
        "report_template",
        "sequence",
        "code",
        "code_system",
        "label",
        "units",
        "type",
        "required",
        "options",  # reverse relation
    }
    assert expected_fields.issubset(field_names)


def test_imaging_option_db_table_name() -> None:
    """Ensure the model uses the correct database table."""
    assert (
        ImagingReportTemplateFieldOption._meta.db_table
        == "canvas_sdk_data_data_integration_imagingreporttmplfieldopt_001"
    )


def test_imaging_option_model_fields() -> None:
    """Ensure all expected fields are defined."""
    field_names = {f.name for f in ImagingReportTemplateFieldOption._meta.get_fields()}
    expected_fields = {"dbid", "field", "label", "key"}
    assert expected_fields.issubset(field_names)


def test_queryset_has_active_method() -> None:
    """Ensure the active() method exists and is callable."""
    assert hasattr(ImagingReportTemplateQuerySet, "active")
    assert callable(ImagingReportTemplateQuerySet.active)


def test_queryset_has_search_method() -> None:
    """Ensure the search() method exists and is callable."""
    assert hasattr(ImagingReportTemplateQuerySet, "search")
    assert callable(ImagingReportTemplateQuerySet.search)


def test_queryset_has_custom_method() -> None:
    """Ensure the custom() method exists and is callable."""
    assert hasattr(ImagingReportTemplateQuerySet, "custom")
    assert callable(ImagingReportTemplateQuerySet.custom)


def test_queryset_has_builtin_method() -> None:
    """Ensure the builtin() method exists and is callable."""
    assert hasattr(ImagingReportTemplateQuerySet, "builtin")
    assert callable(ImagingReportTemplateQuerySet.builtin)


def test_objects_manager_is_queryset_type() -> None:
    """Ensure the objects manager returns the correct QuerySet type."""
    assert ImagingReportTemplate.objects.all().__class__.__name__ == "ImagingReportTemplateQuerySet"
