# SpecialtyReportTemplate Test Data Setup Guide

## Overview

This guide explains how to set up test data for `SpecialtyReportTemplate` API tests using the Django management command `setup_specialty_template_test_data`.

## Purpose

The test data is required for manual testing of the `speciality_report_explorer` plugin in the `canvas-plugins` service. The command creates 5 test templates with various configurations, including fields and field options, to cover all test scenarios.

## Prerequisites

- Docker container `home-app-web` must be running
- Database migrations must be up to date
- Access to the `home-app` directory

## Command Code Reference

The following is a reference implementation of the Django management command that should be created in `home-app`. The command should be placed at:

```
home-app/data_integration/management/commands/setup_specialty_template_test_data.py
```

**Note:** This code is provided here as a reference. The actual command should be implemented in the `home-app` service.

Here is the complete Django management command code:

```python
import uuid

from typing import Any

from django.core.management.base import BaseCommand

from data_integration.models.specialty_report_template import (
    SpecialtyReportTemplate,
    SpecialtyReportTemplateField,
    SpecialtyReportTemplateFieldOption,
)

class Command(BaseCommand):
    help = "Set up test data for SpecialtyReportTemplate SDK tests"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing test data before creating new data",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options["reset"]:
            self._delete_test_data()

        template_count = 0
        field_count = 0
        option_count = 0

        # Create templates
        cardio1, created = self._create_cardiology_template_1()
        if created:
            template_count += 1

        cardio2, created = self._create_cardiology_template_2()
        if created:
            template_count += 1

        cardio3, created = self._create_cardiology_template_3()
        if created:
            template_count += 1

        derm1, created = self._create_dermatology_template()
        if created:
            template_count += 1

        empty1, created = self._create_empty_template()
        if created:
            template_count += 1

        # Create fields for Cardiology Template #1
        field1, created = self._create_field_1(report_template=cardio1)
        if created:
            field_count += 1

        field2, created = self._create_field_2(report_template=cardio1)
        if created:
            field_count += 1

        field3, created = self._create_field_3(report_template=cardio1)
        if created:
            field_count += 1

        field4, created = self._create_field_4(report_template=cardio1)
        if created:
            field_count += 1

        field5, created = self._create_field_5(report_template=cardio1)
        if created:
            field_count += 1

        field6, created = self._create_field_6(report_template=cardio1)
        if created:
            field_count += 1

        # Create options for Field #2 (Assessment - select)
        option_count += self._create_assessment_options(field2)

        # Create options for Field #4 (Recommendation - radio)
        option_count += self._create_recommendation_options(field4)

        # Report results
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully set up test data:\n"
                f"  - {template_count} templates\n"
                f"  - {field_count} fields\n"
                f"  - {option_count} options"
            )
        )

    def _delete_test_data(self) -> None:
        """Delete existing test data identified by TEST_ prefix."""
        deleted_options = SpecialtyReportTemplateFieldOption.objects.filter(
            field__report_template__code__startswith="TEST_"
        ).delete()[0]

        deleted_fields = SpecialtyReportTemplateField.objects.filter(
            report_template__code__startswith="TEST_"
        ).delete()[0]

        deleted_templates = SpecialtyReportTemplate.objects.filter(
            code__startswith="TEST_"
        ).delete()[0]

        self.stdout.write(
            self.style.WARNING(
                f"Deleted existing test data:\n"
                f"  - {deleted_templates} templates\n"
                f"  - {deleted_fields} fields\n"
                f"  - {deleted_options} options"
            )
        )

    def _create_cardiology_template_1(self) -> tuple[SpecialtyReportTemplate, bool]:
        """Create TEST_CARD001 - Active, builtin, Cardiology template with fields."""
        template, created = SpecialtyReportTemplate.objects.get_or_create(
            code="TEST_CARD001",
            defaults={
                "externally_exposable_id": uuid.uuid4(),
                "name": "Cardiology Consultation Report",
                "code_system": "http://example.com/codes",
                "search_keywords": "cardiology cardiac heart cardiovascular",
                "active": True,
                "custom": False,
                "search_as": "cardiology",
                "specialty_name": "Cardiology",
                "specialty_code": "207RC0000X",
                "specialty_code_system": "http://nucc.org/provider-taxonomy",
            },
        )
        return template, created

    def _create_cardiology_template_2(self) -> tuple[SpecialtyReportTemplate, bool]:
        """Create TEST_CARD002 - Active, custom, Cardiology template."""
        template, created = SpecialtyReportTemplate.objects.get_or_create(
            code="TEST_CARD002",
            defaults={
                "externally_exposable_id": uuid.uuid4(),
                "name": "Custom Cardiology Template",
                "code_system": "http://example.com/codes",
                "search_keywords": "cardiac heart",
                "active": True,
                "custom": True,  # Custom template
                "search_as": "cardiac",
                "specialty_name": "Cardiology",
                "specialty_code": "207RC0000X",
                "specialty_code_system": "http://nucc.org/provider-taxonomy",
            },
        )
        return template, created

    def _create_cardiology_template_3(self) -> tuple[SpecialtyReportTemplate, bool]:
        """Create TEST_CARD003 - Inactive, builtin, Cardiology template."""
        template, created = SpecialtyReportTemplate.objects.get_or_create(
            code="TEST_CARD003",
            defaults={
                "externally_exposable_id": uuid.uuid4(),
                "name": "Inactive Cardiology Template",
                "code_system": "http://example.com/codes",
                "search_keywords": "cardiology",
                "active": False,  # Inactive template
                "custom": False,
                "search_as": "cardiology",
                "specialty_name": "Cardiology",
                "specialty_code": "207RC0000X",
                "specialty_code_system": "http://nucc.org/provider-taxonomy",
            },
        )
        return template, created

    def _create_dermatology_template(self) -> tuple[SpecialtyReportTemplate, bool]:
        """Create TEST_DERM001 - Active, builtin, Dermatology template."""
        template, created = SpecialtyReportTemplate.objects.get_or_create(
            code="TEST_DERM001",
            defaults={
                "externally_exposable_id": uuid.uuid4(),
                "name": "Dermatology Consultation Report",
                "code_system": "http://example.com/codes",
                "search_keywords": "dermatology skin",
                "active": True,
                "custom": False,
                "search_as": "dermatology",
                "specialty_name": "Dermatology",
                "specialty_code": "207ND0100X",  # Different specialty code
                "specialty_code_system": "http://nucc.org/provider-taxonomy",
            },
        )
        return template, created

    def _create_empty_template(self) -> tuple[SpecialtyReportTemplate, bool]:
        """Create TEST_EMPTY001 - Active, builtin, General template (edge case)."""
        template, created = SpecialtyReportTemplate.objects.get_or_create(
            code="TEST_EMPTY001",
            defaults={
                "externally_exposable_id": uuid.uuid4(),
                "name": "Empty Template",
                "code_system": "http://example.com/codes",
                "search_keywords": "empty",
                "active": True,
                "custom": False,
                "search_as": "empty",
                "specialty_name": "General",
                "specialty_code": "208D00000X",  # Different specialty code
                "specialty_code_system": "http://nucc.org/provider-taxonomy",
            },
        )
        return template, created

    def _create_field_1(
        self, report_template: SpecialtyReportTemplate
    ) -> tuple[SpecialtyReportTemplateField, bool]:
        """Create Chief Complaint field (sequence 1)."""
        field, created = SpecialtyReportTemplateField.objects.get_or_create(
            report_template=report_template,
            sequence=1,
            defaults={
                "code": "TEST_CC",
                "code_system": "http://loinc.org",
                "label": "Chief Complaint",
                "units": None,
                "type": "text",
                "required": True,
            },
        )
        return field, created

    def _create_field_2(
        self, report_template: SpecialtyReportTemplate
    ) -> tuple[SpecialtyReportTemplateField, bool]:
        """Create Assessment field (sequence 2) - has options."""
        field, created = SpecialtyReportTemplateField.objects.get_or_create(
            report_template=report_template,
            sequence=2,
            defaults={
                "code": "TEST_ASSESS",
                "code_system": "http://loinc.org",
                "label": "Assessment",
                "units": None,
                "type": "select",
                "required": True,
            },
        )
        return field, created

    def _create_field_3(
        self, report_template: SpecialtyReportTemplate
    ) -> tuple[SpecialtyReportTemplateField, bool]:
        """Create Ejection Fraction field (sequence 3)."""
        field, created = SpecialtyReportTemplateField.objects.get_or_create(
            report_template=report_template,
            sequence=3,
            defaults={
                "code": "TEST_EF",
                "code_system": "http://loinc.org",
                "label": "Ejection Fraction",
                "units": "%",
                "type": "float",
                "required": False,
            },
        )
        return field, created

    def _create_field_4(
        self, report_template: SpecialtyReportTemplate
    ) -> tuple[SpecialtyReportTemplateField, bool]:
        """Create Recommendation field (sequence 4) - has options."""
        field, created = SpecialtyReportTemplateField.objects.get_or_create(
            report_template=report_template,
            sequence=4,
            defaults={
                "code": None,
                "code_system": "http://example.com",
                "label": "Recommendation",
                "units": None,
                "type": "radio",
                "required": False,
            },
        )
        return field, created

    def _create_field_5(
        self, report_template: SpecialtyReportTemplate
    ) -> tuple[SpecialtyReportTemplateField, bool]:
        """Create Notes field (sequence 5)."""
        field, created = SpecialtyReportTemplateField.objects.get_or_create(
            report_template=report_template,
            sequence=5,
            defaults={
                "code": None,
                "code_system": "http://example.com",
                "label": "Notes",
                "units": None,
                "type": "text",
                "required": False,
            },
        )
        return field, created

    def _create_field_6(
        self, report_template: SpecialtyReportTemplate
    ) -> tuple[SpecialtyReportTemplateField, bool]:
        """Create Select Without Options field (sequence 6) - edge case."""
        field, created = SpecialtyReportTemplateField.objects.get_or_create(
            report_template=report_template,
            sequence=6,
            defaults={
                "code": None,
                "code_system": "http://example.com",
                "label": "Select Without Options",
                "units": None,
                "type": "select",
                "required": False,
            },
        )
        return field, created

    def _create_assessment_options(
        self, field: SpecialtyReportTemplateField
    ) -> int:
        """Create 3 options for Assessment field."""
        count = 0
        options_data = [
            {"label": "Normal", "key": "TEST_NORMAL"},
            {"label": "Abnormal", "key": "TEST_ABNORMAL"},
            {"label": "Requires Follow-up", "key": "TEST_FOLLOWUP"},
        ]

        for option_data in options_data:
            _, created = SpecialtyReportTemplateFieldOption.objects.get_or_create(
                field=field,
                key=option_data["key"],
                defaults={"label": option_data["label"]},
            )
            if created:
                count += 1

        return count

    def _create_recommendation_options(
        self, field: SpecialtyReportTemplateField
    ) -> int:
        """Create 3 options for Recommendation field."""
        count = 0
        options_data = [
            {"label": "Continue Current Treatment", "key": "TEST_CONTINUE"},
            {"label": "Modify Treatment", "key": "TEST_MODIFY"},
            {"label": "Discontinue Treatment", "key": "TEST_DISCONTINUE"},
        ]

        for option_data in options_data:
            _, created = SpecialtyReportTemplateFieldOption.objects.get_or_create(
                field=field,
                key=option_data["key"],
                defaults={"label": option_data["label"]},
            )
            if created:
                count += 1

        return count
```

## Usage

### Basic Usage - Create Test Data

To create the test data, run:

```bash
docker exec home-app-web python manage.py setup_specialty_template_test_data
```

**Expected Output:**

```
Successfully set up test data:
  - 5 templates
  - 6 fields
  - 6 options
```

### Reset and Recreate Test Data

To delete existing test data and recreate it fresh, use the `--reset` flag:

```bash
docker exec home-app-web python manage.py setup_specialty_template_test_data --reset
```

**Expected Output:**

```
Deleted existing test data:
  - 5 templates
  - 6 fields
  - 6 options
Successfully set up test data:
  - 5 templates
  - 6 fields
  - 6 options
```

### Idempotency

The command is idempotent - running it multiple times without `--reset` will not create duplicate data. It uses Django's `get_or_create()` method to check if templates, fields, and options already exist before creating them.

## Verification

After running the command, you can verify the data was created correctly using Django shell:

### Check Templates

```bash
docker exec home-app-web python manage.py shell -c "
from data_integration.models.specialty_report_template import SpecialtyReportTemplate
templates = SpecialtyReportTemplate.objects.filter(code__startswith='TEST_').order_by('code')
print(f'Found {templates.count()} templates:')
for t in templates:
    print(f'  {t.code}: {t.name} (active={t.active}, custom={t.custom}, specialty={t.specialty_code})')
"
```

### Check Fields for TEST_CARD001

```bash
docker exec home-app-web python manage.py shell -c "
from data_integration.models.specialty_report_template import SpecialtyReportTemplate
template = SpecialtyReportTemplate.objects.get(code='TEST_CARD001')
print(f'Fields for {template.code}: {template.fields.count()}')
for field in template.fields.all().order_by('sequence'):
    print(f'  {field.sequence}. {field.label} ({field.type}, required={field.required}, options={field.options.count()})')
"
```

### Check Field Options

```bash
docker exec home-app-web python manage.py shell -c "
from data_integration.models.specialty_report_template import SpecialtyReportTemplateField
assessment_field = SpecialtyReportTemplateField.objects.get(report_template__code='TEST_CARD001', sequence=2)
print('Assessment field options:')
for option in assessment_field.options.all():
    print(f'  - {option.label} (key: {option.key})')
"
```

### Verify UUIDs

```bash
docker exec home-app-web python manage.py shell -c "
from data_integration.models.specialty_report_template import SpecialtyReportTemplate
template = SpecialtyReportTemplate.objects.get(code='TEST_CARD001')
print(f'Template {template.code} externally_exposable_id: {template.externally_exposable_id}')
"
```

## Test Coverage

This test data covers the following test scenarios:

1. **Basic Data Fetching**: All 5 templates should be returned

2. **Active Filter**: 4 active templates (TEST_CARD001, TEST_CARD002, TEST_DERM001, TEST_EMPTY001)

3. **Search Filter**:
   - "cardiology" → TEST_CARD001, TEST_CARD003
   - "cardiac" → TEST_CARD001, TEST_CARD002
   - "heart" → TEST_CARD001, TEST_CARD002

4. **Custom/Builtin Filter**:
   - Custom → TEST_CARD002 (1 custom)
   - Builtin → TEST_CARD001, TEST_CARD003, TEST_DERM001, TEST_EMPTY001 (4 builtin)

5. **Specialty Code Filter**:
   - "207RC0000X" → TEST_CARD001, TEST_CARD002, TEST_CARD003 (3 Cardiology)
   - "207ND0100X" → TEST_DERM001 (1 Dermatology)

6. **Fields and Options**: TEST_CARD001 has 6 fields, 2 fields have options (6 total options)

7. **Edge Cases**:
   - TEST_EMPTY001 (no fields)
   - Select Without Options field (select type with no options)

## Cleanup

To remove all test data, use the `--reset` flag and then manually delete:

```bash
docker exec home-app-web python manage.py shell -c "
from data_integration.models.specialty_report_template import (
    SpecialtyReportTemplate,
    SpecialtyReportTemplateField,
    SpecialtyReportTemplateFieldOption
)
SpecialtyReportTemplateFieldOption.objects.filter(field__report_template__code__startswith='TEST_').delete()
SpecialtyReportTemplateField.objects.filter(report_template__code__startswith='TEST_').delete()
SpecialtyReportTemplate.objects.filter(code__startswith='TEST_').delete()
print('Test data deleted')
"
```

Or simply use:

```bash
docker exec home-app-web python manage.py setup_specialty_template_test_data --reset
```

Then manually delete the templates if you want to remove them completely.

## Troubleshooting

### Command Not Found

If you get a "Command not found" error, ensure:

- You're running the command from the `home-app` directory
- The Docker container `home-app-web` is running
- The management command file exists at the correct path

### Database Connection Errors

If you encounter database connection errors:

- Verify the Docker container is running: `docker ps | grep home-app-web`
- Check database migrations are up to date: `docker exec home-app-web python manage.py migrate`

### Duplicate Data Warnings

The command uses `get_or_create()` which prevents duplicates. If you see warnings about existing data, use the `--reset` flag to clean up first.

## Related Files

- Management Command: `home-app/data_integration/management/commands/setup_specialty_template_test_data.py`
- Models: `home-app/data_integration/models/specialty_report_template.py`
- Database Views: `home-app/plugin_io/database_views.py`

## Notes

- All template codes start with "TEST_" prefix for easy identification
- The `externally_exposable_id` field is automatically generated as a UUID for each template
- Foreign key relationships use Django ORM relationships, not raw database IDs
- Timestamps (`created`, `modified`) are automatically handled by Django
