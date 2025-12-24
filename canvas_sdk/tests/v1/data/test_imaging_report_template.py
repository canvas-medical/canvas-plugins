from canvas_sdk.v1.data.imaging import (
    ImagingReportTemplate,
    ImagingReportTemplateField,
    ImagingReportTemplateFieldOption,
    ImagingReportTemplateQuerySet,
)


class TestImagingReportTemplateModel:
    """Tests for ImagingReportTemplate model."""

    def test_db_table_name(self) -> None:
        """Ensure the model uses the correct database table."""
        assert (
            ImagingReportTemplate._meta.db_table
            == "canvas_sdk_data_data_integration_imagingreporttemplate_001"
        )

    def test_model_fields(self) -> None:
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


class TestImagingReportTemplateFieldModel:
    """Tests for ImagingReportTemplateField model."""

    def test_db_table_name(self) -> None:
        """Ensure the model uses the correct database table."""
        assert (
            ImagingReportTemplateField._meta.db_table
            == "canvas_sdk_data_data_integration_imagingreporttemplatefield_001"
        )

    def test_model_fields(self) -> None:
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


class TestImagingReportTemplateFieldOptionModel:
    """Tests for ImagingReportTemplateFieldOption model."""

    def test_db_table_name(self) -> None:
        """Ensure the model uses the correct database table."""
        assert (
            ImagingReportTemplateFieldOption._meta.db_table
            == "canvas_sdk_data_data_integration_imagingreporttmplfieldopt_001"
        )

    def test_model_fields(self) -> None:
        """Ensure all expected fields are defined."""
        field_names = {f.name for f in ImagingReportTemplateFieldOption._meta.get_fields()}
        expected_fields = {"dbid", "field", "label", "key"}
        assert expected_fields.issubset(field_names)


class TestImagingReportTemplateQuerySet:
    """Tests for ImagingReportTemplateQuerySet methods."""

    def test_queryset_has_active_method(self) -> None:
        """Ensure the active() method exists and is callable."""
        assert hasattr(ImagingReportTemplateQuerySet, "active")
        assert callable(getattr(ImagingReportTemplateQuerySet, "active"))

    def test_queryset_has_search_method(self) -> None:
        """Ensure the search() method exists and is callable."""
        assert hasattr(ImagingReportTemplateQuerySet, "search")
        assert callable(getattr(ImagingReportTemplateQuerySet, "search"))

    def test_queryset_has_custom_method(self) -> None:
        """Ensure the custom() method exists and is callable."""
        assert hasattr(ImagingReportTemplateQuerySet, "custom")
        assert callable(getattr(ImagingReportTemplateQuerySet, "custom"))

    def test_queryset_has_builtin_method(self) -> None:
        """Ensure the builtin() method exists and is callable."""
        assert hasattr(ImagingReportTemplateQuerySet, "builtin")
        assert callable(getattr(ImagingReportTemplateQuerySet, "builtin"))

    def test_objects_manager_is_queryset_type(self) -> None:
        """Ensure the objects manager returns the correct QuerySet type."""
        assert ImagingReportTemplate.objects.all().__class__.__name__ == "ImagingReportTemplateQuerySet"
