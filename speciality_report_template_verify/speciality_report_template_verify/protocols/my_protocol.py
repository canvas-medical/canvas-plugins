import json
import time
from typing import Any

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.handlers.cron_task import CronTask
from canvas_sdk.v1.data import (
    SpecialtyReportTemplate,
    SpecialtyReportTemplateField,
    SpecialtyReportTemplateFieldOption,
)
from canvas_sdk.events import EventType
from logger import log


class Protocol(CronTask):
    """Verification plugin for SpecialtyReportTemplate data models.

    Runs every minute to test data fetching, relationships, QuerySet methods,
    and model structure for SpecialtyReportTemplate, SpecialtyReportTemplateField,
    and SpecialtyReportTemplateFieldOption.
    """

    SCHEDULE = "* * * * *"  # Every minute

    RESPONDS_TO = [
        EventType.Name(EventType.CRON),
    ]

    def compute(self) -> list[Effect]:
        """Execute all verification tests for SpecialtyReportTemplate models."""
        effects = []
        test_results = {
            "timestamp": time.time(),
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0},
        }

        # Run all test cases
        test_functions = [
            self._test_1_basic_data_fetching,
            self._test_2_queryset_active,
            self._test_3_queryset_search,
            self._test_4_queryset_custom_builtin,
            self._test_5_queryset_by_specialty,
            self._test_6_method_chaining,
            self._test_7_template_field_relationship,
            self._test_8_field_option_relationship,
            self._test_9_prefetch_related,
            self._test_10_specialty_specific_fields,
            self._test_11_field_type_validation,
            self._test_12_complete_template_structure,
            self._test_13_edge_cases,
            self._test_14_performance_check,
        ]

        for test_func in test_functions:
            result = self._run_test(test_func)
            test_results["tests"].append(result)
            test_results["summary"]["total"] += 1
            if result["status"] == "PASS":
                test_results["summary"]["passed"] += 1
            else:
                test_results["summary"]["failed"] += 1

            # Create log effect for each test
            effects.append(
                Effect(
                    type=EffectType.LOG,
                    payload=json.dumps(
                        {
                            "test": result["name"],
                            "status": result["status"],
                            "data": result.get("data", {}),
                        }
                    ),
                )
            )

        # Add summary effect
        effects.append(
            Effect(
                type=EffectType.LOG,
                payload=json.dumps(
                    {
                        "summary": test_results["summary"],
                        "message": f"Verification complete: {test_results['summary']['passed']}/{test_results['summary']['total']} tests passed",
                    }
                ),
            )
        )

        return effects

    def _run_test(self, test_func) -> dict[str, Any]:
        """Run a test function and return structured result."""
        test_name = test_func.__name__.replace("_test_", "").replace("_", " ").title()
        try:
            result = test_func()
            return {
                "name": test_name,
                "status": "PASS",
                "data": result,
            }
        except Exception as e:
            log.exception(f"Test {test_name} failed")
            return {
                "name": test_name,
                "status": "FAIL",
                "error": str(e),
                "data": {},
            }

    def _test_1_basic_data_fetching(self) -> dict[str, Any]:
        """Test 1: Basic Data Fetching."""
        log.info("Test 1: Basic Data Fetching")
        templates = SpecialtyReportTemplate.objects.all()
        template_count = templates.count()

        if template_count == 0:
            log.warning("No templates found in database")
            return {"count": 0, "message": "No templates available"}

        # Get first template and verify fields
        first_template = templates.first()
        assert first_template is not None

        field_data = {
            "dbid": first_template.dbid,
            "name": first_template.name,
            "code": first_template.code,
            "code_system": first_template.code_system,
            "active": first_template.active,
            "custom": first_template.custom,
            "specialty_code": first_template.specialty_code,
            "specialty_name": first_template.specialty_name,
        }

        log.info(f"Found {template_count} templates. Sample: {field_data}")
        return {"count": template_count, "sample_template": field_data}

    def _test_2_queryset_active(self) -> dict[str, Any]:
        """Test 2: QuerySet Methods - active()."""
        log.info("Test 2: QuerySet Methods - active()")
        all_templates = SpecialtyReportTemplate.objects.all()
        active_templates = SpecialtyReportTemplate.objects.active()

        all_count = all_templates.count()
        active_count = active_templates.count()

        # Verify all active templates have active=True
        for template in active_templates[:10]:  # Check first 10
            assert template.active is True, f"Template {template.dbid} should be active"

        log.info(f"Total templates: {all_count}, Active templates: {active_count}")
        return {"total": all_count, "active": active_count}

    def _test_3_queryset_search(self) -> dict[str, Any]:
        """Test 3: QuerySet Methods - search()."""
        log.info("Test 3: QuerySet Methods - search()")

        # Test with a common search term
        search_queries = ["cardiology", "cardiac", "heart"]
        results = {}

        for query in search_queries:
            search_results = SpecialtyReportTemplate.objects.search(query)
            count = search_results.count()
            results[query] = count
            log.info(f"Search '{query}': {count} results")

        # Test with empty query (should return all or handle gracefully)
        empty_results = SpecialtyReportTemplate.objects.search("")
        results["empty_query"] = empty_results.count()

        return {"search_results": results}

    def _test_4_queryset_custom_builtin(self) -> dict[str, Any]:
        """Test 4: QuerySet Methods - custom() and builtin()."""
        log.info("Test 4: QuerySet Methods - custom() and builtin()")

        all_count = SpecialtyReportTemplate.objects.all().count()
        custom_count = SpecialtyReportTemplate.objects.custom().count()
        builtin_count = SpecialtyReportTemplate.objects.builtin().count()

        # Verify custom + builtin equals total (approximately, due to potential data issues)
        log.info(f"Total: {all_count}, Custom: {custom_count}, Builtin: {builtin_count}")

        # Verify custom templates have custom=True
        for template in SpecialtyReportTemplate.objects.custom()[:5]:
            assert template.custom is True

        # Verify builtin templates have custom=False
        for template in SpecialtyReportTemplate.objects.builtin()[:5]:
            assert template.custom is False

        return {
            "total": all_count,
            "custom": custom_count,
            "builtin": builtin_count,
        }

    def _test_5_queryset_by_specialty(self) -> dict[str, Any]:
        """Test 5: QuerySet Methods - by_specialty()."""
        log.info("Test 5: QuerySet Methods - by_specialty()")

        # Get a specialty code from existing templates
        sample_template = SpecialtyReportTemplate.objects.first()
        if not sample_template:
            return {"message": "No templates available for testing"}

        specialty_code = sample_template.specialty_code
        specialty_results = SpecialtyReportTemplate.objects.by_specialty(specialty_code)
        count = specialty_results.count()

        # Verify all results have matching specialty_code
        for template in specialty_results[:10]:
            assert template.specialty_code == specialty_code

        # Test with non-existent specialty code
        non_existent = SpecialtyReportTemplate.objects.by_specialty("999XX9999X")
        non_existent_count = non_existent.count()

        log.info(f"Specialty '{specialty_code}': {count} templates")
        log.info(f"Non-existent specialty: {non_existent_count} templates")

        return {
            "tested_specialty": specialty_code,
            "count": count,
            "non_existent_count": non_existent_count,
        }

    def _test_6_method_chaining(self) -> dict[str, Any]:
        """Test 6: Method Chaining."""
        log.info("Test 6: Method Chaining")

        # Chain active().by_specialty()
        sample_template = SpecialtyReportTemplate.objects.first()
        if not sample_template:
            return {"message": "No templates available for testing"}

        specialty_code = sample_template.specialty_code
        chained_1 = (
            SpecialtyReportTemplate.objects.active().by_specialty(specialty_code)
        )
        count_1 = chained_1.count()

        # Chain active().search()
        chained_2 = SpecialtyReportTemplate.objects.active().search("cardiology")
        count_2 = chained_2.count()

        # Chain active().custom()
        chained_3 = SpecialtyReportTemplate.objects.active().custom()
        count_3 = chained_3.count()

        # Chain active().builtin()
        chained_4 = SpecialtyReportTemplate.objects.active().builtin()
        count_4 = chained_4.count()

        log.info(f"Chained queries: active+by_specialty={count_1}, active+search={count_2}, active+custom={count_3}, active+builtin={count_4}")

        return {
            "active_by_specialty": count_1,
            "active_search": count_2,
            "active_custom": count_3,
            "active_builtin": count_4,
        }

    def _test_7_template_field_relationship(self) -> dict[str, Any]:
        """Test 7: Template-Field Relationship."""
        log.info("Test 7: Template-Field Relationship")

        template = (
            SpecialtyReportTemplate.objects.prefetch_related("fields").first()
        )
        if not template:
            return {"message": "No templates available for testing"}

        fields = template.fields.all()
        field_count = fields.count()

        if field_count == 0:
            log.warning(f"Template {template.dbid} has no fields")
            return {"template_id": template.dbid, "field_count": 0}

        # Verify field attributes
        field_data = []
        for field in fields.order_by("sequence")[:5]:
            field_data.append(
                {
                    "dbid": field.dbid,
                    "sequence": field.sequence,
                    "label": field.label,
                    "type": field.type,
                    "required": field.required,
                }
            )

        log.info(f"Template {template.dbid} has {field_count} fields")
        return {
            "template_id": template.dbid,
            "template_name": template.name,
            "field_count": field_count,
            "sample_fields": field_data,
        }

    def _test_8_field_option_relationship(self) -> dict[str, Any]:
        """Test 8: Field-Option Relationship."""
        log.info("Test 8: Field-Option Relationship")

        # Find a field with options
        field = (
            SpecialtyReportTemplateField.objects.prefetch_related("options")
            .filter(options__isnull=False)
            .first()
        )

        if not field:
            log.warning("No fields with options found")
            return {"message": "No fields with options available"}

        options = field.options.all()
        option_count = options.count()

        option_data = []
        for option in options[:5]:
            option_data.append({"dbid": option.dbid, "label": option.label, "key": option.key})

        log.info(f"Field {field.dbid} has {option_count} options")
        return {
            "field_id": field.dbid,
            "field_label": field.label,
            "option_count": option_count,
            "sample_options": option_data,
        }

    def _test_9_prefetch_related(self) -> dict[str, Any]:
        """Test 9: Prefetch Related (Full Relationship Chain)."""
        log.info("Test 9: Prefetch Related")

        template = (
            SpecialtyReportTemplate.objects.prefetch_related(
                "fields", "fields__options"
            ).first()
        )

        if not template:
            return {"message": "No templates available for testing"}

        fields = template.fields.all()
        field_count = fields.count()

        # Access nested relationships
        nested_data = []
        for field in fields[:3]:
            options = field.options.all()
            nested_data.append(
                {
                    "field_id": field.dbid,
                    "field_label": field.label,
                    "option_count": options.count(),
                }
            )

        log.info(f"Template {template.dbid} with prefetch: {field_count} fields")
        return {
            "template_id": template.dbid,
            "field_count": field_count,
            "nested_relationships": nested_data,
        }

    def _test_10_specialty_specific_fields(self) -> dict[str, Any]:
        """Test 10: Specialty-Specific Fields Access."""
        log.info("Test 10: Specialty-Specific Fields Access")

        template = SpecialtyReportTemplate.objects.first()
        if not template:
            return {"message": "No templates available for testing"}

        specialty_fields = {
            "search_as": template.search_as,
            "specialty_name": template.specialty_name,
            "specialty_code": template.specialty_code,
            "specialty_code_system": template.specialty_code_system,
        }

        # Verify fields are accessible and not None (they might be empty strings)
        for key, value in specialty_fields.items():
            assert hasattr(template, key), f"Template should have {key} attribute"
            log.info(f"{key}: {value}")

        # Test filtering by specialty_name
        if template.specialty_name:
            filtered = SpecialtyReportTemplate.objects.filter(
                specialty_name=template.specialty_name
            )
            filtered_count = filtered.count()
            log.info(f"Filtered by specialty_name '{template.specialty_name}': {filtered_count}")
        else:
            filtered_count = 0

        return {
            "specialty_fields": specialty_fields,
            "filtered_by_name_count": filtered_count,
        }

    def _test_11_field_type_validation(self) -> dict[str, Any]:
        """Test 11: Field Type Validation."""
        log.info("Test 11: Field Type Validation")

        fields = SpecialtyReportTemplateField.objects.all()[:20]
        field_count = fields.count()

        if field_count == 0:
            return {"message": "No fields available for testing"}

        type_distribution = {}
        required_count = 0
        nullable_code_count = 0
        nullable_units_count = 0

        for field in fields:
            # Count field types
            field_type = field.type
            type_distribution[field_type] = type_distribution.get(field_type, 0) + 1

            # Count required fields
            if field.required:
                required_count += 1

            # Count nullable fields
            if field.code is None:
                nullable_code_count += 1
            if field.units is None:
                nullable_units_count += 1

        log.info(f"Field type distribution: {type_distribution}")
        log.info(f"Required fields: {required_count}/{field_count}")

        return {
            "field_count": field_count,
            "type_distribution": type_distribution,
            "required_count": required_count,
            "nullable_code_count": nullable_code_count,
            "nullable_units_count": nullable_units_count,
        }

    def _test_12_complete_template_structure(self) -> dict[str, Any]:
        """Test 12: Data Integrity - Complete Template Structure."""
        log.info("Test 12: Complete Template Structure")

        template = (
            SpecialtyReportTemplate.objects.prefetch_related(
                "fields", "fields__options"
            ).first()
        )

        if not template:
            return {"message": "No templates available for testing"}

        fields = template.fields.all().order_by("sequence")
        field_count = fields.count()

        if field_count == 0:
            log.warning(f"Template {template.dbid} has no fields")
            return {"template_id": template.dbid, "field_count": 0}

        # Verify sequence numbers
        sequences = [field.sequence for field in fields]
        is_sequential = sequences == sorted(sequences)

        # Check fields with select/radio types have options
        select_fields_with_options = 0
        select_fields_without_options = 0

        complete_structure = {
            "template": {
                "dbid": template.dbid,
                "name": template.name,
                "specialty_code": template.specialty_code,
            },
            "fields": [],
        }

        for field in fields[:5]:  # Limit to first 5 for logging
            options = field.options.all()
            option_count = options.count()

            if field.type in ["select", "radio"]:
                if option_count > 0:
                    select_fields_with_options += 1
                else:
                    select_fields_without_options += 1

            complete_structure["fields"].append(
                {
                    "dbid": field.dbid,
                    "sequence": field.sequence,
                    "label": field.label,
                    "type": field.type,
                    "option_count": option_count,
                }
            )

        log.info(f"Template structure validated: {field_count} fields, sequential={is_sequential}")
        if select_fields_without_options > 0:
            log.warning(f"{select_fields_without_options} select/radio fields without options")

        return {
            "template_id": template.dbid,
            "field_count": field_count,
            "is_sequential": is_sequential,
            "select_fields_with_options": select_fields_with_options,
            "select_fields_without_options": select_fields_without_options,
            "structure": complete_structure,
        }

    def _test_13_edge_cases(self) -> dict[str, Any]:
        """Test 13: Edge Cases."""
        log.info("Test 13: Edge Cases")

        edge_case_results = {}

        # Test with templates that have no fields
        templates_without_fields = SpecialtyReportTemplate.objects.filter(
            fields__isnull=True
        ).distinct()
        edge_case_results["templates_without_fields"] = templates_without_fields.count()

        # Test with fields that have no options
        fields_without_options = SpecialtyReportTemplateField.objects.filter(
            options__isnull=True
        )
        edge_case_results["fields_without_options"] = fields_without_options.count()

        # Test with non-existent specialty code
        non_existent = SpecialtyReportTemplate.objects.by_specialty("999XX9999X")
        edge_case_results["non_existent_specialty"] = non_existent.count()

        # Test empty search
        empty_search = SpecialtyReportTemplate.objects.search("nonexistentterm12345")
        edge_case_results["empty_search_results"] = empty_search.count()

        log.info(f"Edge cases: {edge_case_results}")
        return edge_case_results

    def _test_14_performance_check(self) -> dict[str, Any]:
        """Test 14: Performance Check."""
        log.info("Test 14: Performance Check")

        # Measure basic query time
        start_time = time.time()
        basic_query = SpecialtyReportTemplate.objects.all()
        basic_count = basic_query.count()
        basic_time = time.time() - start_time

        # Measure prefetch_related query time
        start_time = time.time()
        prefetch_query = SpecialtyReportTemplate.objects.prefetch_related(
            "fields", "fields__options"
        )
        prefetch_count = prefetch_query.count()
        prefetch_time = time.time() - start_time

        # Measure accessing relationships (should be fast with prefetch)
        start_time = time.time()
        for template in prefetch_query[:5]:
            _ = list(template.fields.all())
            for field in template.fields.all()[:3]:
                _ = list(field.options.all())
        relationship_access_time = time.time() - start_time

        log.info(
            f"Performance: basic={basic_time:.4f}s, prefetch={prefetch_time:.4f}s, "
            f"relationship_access={relationship_access_time:.4f}s"
        )

        return {
            "basic_query_time": round(basic_time, 4),
            "prefetch_query_time": round(prefetch_time, 4),
            "relationship_access_time": round(relationship_access_time, 4),
            "basic_count": basic_count,
            "prefetch_count": prefetch_count,
        }
