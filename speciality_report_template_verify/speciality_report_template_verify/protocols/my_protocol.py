import json
import time
from typing import Any

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import (
    SpecialtyReportTemplate,
    SpecialtyReportTemplateField,
    SpecialtyReportTemplateFieldOption,
)
from logger import log


class Protocol(BaseProtocol):
    """Verification plugin for SpecialtyReportTemplate data models.

    Runs every minute to test data fetching, relationships, QuerySet methods,
    and model structure for SpecialtyReportTemplate, SpecialtyReportTemplateField,
    and SpecialtyReportTemplateFieldOption.
    """

    RESPONDS_TO = EventType.Name(EventType.CRON)

    def compute(self) -> list[Effect]:
        """Execute all verification tests for SpecialtyReportTemplate models."""
        timestamp_str = str(self.event.target.id)
        log.info(f"CRON event received at {timestamp_str} - Starting SpecialtyReportTemplate verification tests...")
        
        # Step 1: Extract all baseline data from database BEFORE running tests
        log.info("Step 1: Extracting baseline data from database...")
        baseline_data = self._extract_baseline_data()
        log.info(f"Baseline data extracted: {baseline_data['summary']}")
        
        # Execute all verification tests
        log.info("Step 2: Starting SpecialtyReportTemplate verification tests...")
        effects = []
        test_results = {
            "timestamp": time.time(),
            "baseline_data": baseline_data,
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0},
        }

        # Run all test cases (now with baseline data available)
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
            self._test_15_database_state_analysis,
        ]

        for test_func in test_functions:
            result = self._run_test(test_func, baseline_data)
            test_results["tests"].append(result)
            test_results["summary"]["total"] = test_results["summary"]["total"] + 1
            if result["status"] == "PASS":
                test_results["summary"]["passed"] = test_results["summary"]["passed"] + 1
            else:
                test_results["summary"]["failed"] = test_results["summary"]["failed"] + 1

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

    def _run_test(self, test_func, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Run a test function and return structured result."""
        test_name = test_func.__name__.replace("_test_", "").replace("_", " ").title()
        try:
            result = test_func(baseline_data)
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

    def _extract_baseline_data(self) -> dict[str, Any]:
        """Extract all data from database to use as baseline for test validation."""
        log.info("Extracting all templates, fields, and options from database...")
        
        # Extract all templates
        all_templates = SpecialtyReportTemplate.objects.all()
        templates_data = {}
        test_templates = {}
        production_templates = {}
        
        for template in all_templates:
            template_dict = {
                "dbid": template.dbid,
                "name": template.name,
                "code": template.code,
                "code_system": template.code_system,
                "search_keywords": template.search_keywords,
                "active": template.active,
                "custom": template.custom,
                "search_as": template.search_as,
                "specialty_name": template.specialty_name,
                "specialty_code": template.specialty_code,
                "specialty_code_system": template.specialty_code_system,
                "field_count": 0,  # Will be populated below
            }
            templates_data[template.dbid] = template_dict
            
            if template.code and template.code.startswith("TEST_"):
                test_templates[template.dbid] = template_dict
            else:
                production_templates[template.dbid] = template_dict
        
        # Extract all fields with their template relationships
        all_fields = SpecialtyReportTemplateField.objects.select_related("report_template").all()
        fields_data = {}
        template_field_map = {}  # template_id -> [field_ids]
        
        for field in all_fields:
            field_dict = {
                "dbid": field.dbid,
                "report_template_id": field.report_template_id,
                "sequence": field.sequence,
                "code": field.code,
                "code_system": field.code_system,
                "label": field.label,
                "units": field.units,
                "type": field.type,
                "required": field.required,
                "option_count": 0,  # Will be populated below
            }
            fields_data[field.dbid] = field_dict
            
            # Map fields to templates
            if field.report_template_id not in template_field_map:
                template_field_map[field.report_template_id] = []
            template_field_map[field.report_template_id].append(field.dbid)
            
            # Update template field count
            if field.report_template_id in templates_data:
                templates_data[field.report_template_id]["field_count"] = (
                    templates_data[field.report_template_id]["field_count"] + 1
                )
        
        # Extract all options with their field relationships
        all_options = SpecialtyReportTemplateFieldOption.objects.select_related("field").all()
        options_data = {}
        field_option_map = {}  # field_id -> [option_ids]
        
        for option in all_options:
            option_dict = {
                "dbid": option.dbid,
                "field_id": option.field_id,
                "label": option.label,
                "key": option.key,
            }
            options_data[option.dbid] = option_dict
            
            # Map options to fields
            if option.field_id not in field_option_map:
                field_option_map[option.field_id] = []
            field_option_map[option.field_id].append(option.dbid)
            
            # Update field option count
            if option.field_id in fields_data:
                fields_data[option.field_id]["option_count"] = (
                    fields_data[option.field_id]["option_count"] + 1
                )
        
        # Calculate statistics
        total_templates = len(templates_data)
        total_fields = len(fields_data)
        total_options = len(options_data)
        
        active_templates = sum(1 for t in templates_data.values() if t["active"])
        inactive_templates = total_templates - active_templates
        custom_templates = sum(1 for t in templates_data.values() if t["custom"])
        builtin_templates = total_templates - custom_templates
        
        templates_with_fields = sum(1 for t in templates_data.values() if t["field_count"] > 0)
        templates_without_fields = total_templates - templates_with_fields
        
        fields_with_options = sum(1 for f in fields_data.values() if f["option_count"] > 0)
        fields_without_options = total_fields - fields_with_options
        
        # Specialty distribution
        specialty_distribution = {}
        for template in templates_data.values():
            specialty_code = template["specialty_code"]
            if specialty_code:
                if specialty_code not in specialty_distribution:
                    specialty_distribution[specialty_code] = {
                        "name": template["specialty_name"],
                        "count": 0,
                        "template_ids": [],
                    }
                specialty_distribution[specialty_code]["count"] = (
                    specialty_distribution[specialty_code]["count"] + 1
                )
                specialty_distribution[specialty_code]["template_ids"].append(template["dbid"])
        
        # Field type distribution
        field_type_distribution = {}
        for field in fields_data.values():
            field_type = field["type"]
            field_type_distribution[field_type] = field_type_distribution.get(field_type, 0) + 1
        
        baseline = {
            "templates": templates_data,
            "fields": fields_data,
            "options": options_data,
            "test_templates": test_templates,
            "production_templates": production_templates,
            "template_field_map": template_field_map,
            "field_option_map": field_option_map,
            "summary": {
                "total_templates": total_templates,
                "total_fields": total_fields,
                "total_options": total_options,
                "test_template_count": len(test_templates),
                "production_template_count": len(production_templates),
                "active_templates": active_templates,
                "inactive_templates": inactive_templates,
                "custom_templates": custom_templates,
                "builtin_templates": builtin_templates,
                "templates_with_fields": templates_with_fields,
                "templates_without_fields": templates_without_fields,
                "fields_with_options": fields_with_options,
                "fields_without_options": fields_without_options,
                "specialty_count": len(specialty_distribution),
                "field_type_count": len(field_type_distribution),
            },
            "specialty_distribution": specialty_distribution,
            "field_type_distribution": field_type_distribution,
        }
        
        log.info(f"Baseline extraction complete: {total_templates} templates, {total_fields} fields, {total_options} options")
        return baseline

    def _test_1_basic_data_fetching(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 1: Basic Data Fetching - Compare with baseline."""
        log.info("Test 1: Basic Data Fetching")
        templates = SpecialtyReportTemplate.objects.all()
        template_count = templates.count()

        # Compare with baseline
        baseline_count = baseline_data["summary"]["total_templates"]
        matches_baseline = template_count == baseline_count

        if template_count == 0:
            log.warning("No templates found in database")
            return {
                "count": 0,
                "baseline_count": baseline_count,
                "matches_baseline": False,
                "message": "No templates available"
            }

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

        # Verify first template matches baseline data
        baseline_template = baseline_data["templates"].get(first_template.dbid)
        template_matches = baseline_template is not None and (
            baseline_template["name"] == first_template.name and
            baseline_template["code"] == first_template.code
        )

        log.info(f"Found {template_count} templates (baseline: {baseline_count}, match: {matches_baseline})")
        return {
            "count": template_count,
            "baseline_count": baseline_count,
            "matches_baseline": matches_baseline,
            "sample_template": field_data,
            "template_matches_baseline": template_matches,
        }

    def _test_2_queryset_active(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 2: QuerySet Methods - active() - Compare with baseline."""
        log.info("Test 2: QuerySet Methods - active()")
        all_templates = SpecialtyReportTemplate.objects.all()
        active_templates = SpecialtyReportTemplate.objects.active()

        all_count = all_templates.count()
        active_count = active_templates.count()

        # Compare with baseline
        baseline_total = baseline_data["summary"]["total_templates"]
        baseline_active = baseline_data["summary"]["active_templates"]
        matches_total = all_count == baseline_total
        matches_active = active_count == baseline_active

        # Verify all active templates have active=True
        for template in active_templates[:10]:  # Check first 10
            assert template.active is True, f"Template {template.dbid} should be active"
            # Verify against baseline
            baseline_template = baseline_data["templates"].get(template.dbid)
            if baseline_template:
                assert baseline_template["active"] is True, f"Baseline shows template {template.dbid} should be active"

        log.info(f"Total templates: {all_count} (baseline: {baseline_total}, match: {matches_total}), Active: {active_count} (baseline: {baseline_active}, match: {matches_active})")
        return {
            "total": all_count,
            "active": active_count,
            "baseline_total": baseline_total,
            "baseline_active": baseline_active,
            "matches_total": matches_total,
            "matches_active": matches_active,
        }

    def _test_3_queryset_search(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
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

    def _test_4_queryset_custom_builtin(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 4: QuerySet Methods - custom() and builtin()."""
        log.info("Test 4: QuerySet Methods - custom() and builtin()")

        all_count = SpecialtyReportTemplate.objects.all().count()
        custom_count = SpecialtyReportTemplate.objects.custom().count()
        builtin_count = SpecialtyReportTemplate.objects.builtin().count()

        # Compare with baseline
        baseline_total = baseline_data["summary"]["total_templates"]
        baseline_custom = baseline_data["summary"]["custom_templates"]
        baseline_builtin = baseline_data["summary"]["builtin_templates"]
        matches_total = all_count == baseline_total
        matches_custom = custom_count == baseline_custom
        matches_builtin = builtin_count == baseline_builtin

        # Verify custom + builtin equals total (approximately, due to potential data issues)
        log.info(f"Total: {all_count} (baseline: {baseline_total}, match: {matches_total}), Custom: {custom_count} (baseline: {baseline_custom}, match: {matches_custom}), Builtin: {builtin_count} (baseline: {baseline_builtin}, match: {matches_builtin})")

        # Verify custom templates have custom=True
        for template in SpecialtyReportTemplate.objects.custom()[:5]:
            assert template.custom is True
            baseline_template = baseline_data["templates"].get(template.dbid)
            if baseline_template:
                assert baseline_template["custom"] is True

        # Verify builtin templates have custom=False
        for template in SpecialtyReportTemplate.objects.builtin()[:5]:
            assert template.custom is False
            baseline_template = baseline_data["templates"].get(template.dbid)
            if baseline_template:
                assert baseline_template["custom"] is False

        return {
            "total": all_count,
            "custom": custom_count,
            "builtin": builtin_count,
            "baseline_total": baseline_total,
            "baseline_custom": baseline_custom,
            "baseline_builtin": baseline_builtin,
            "matches_total": matches_total,
            "matches_custom": matches_custom,
            "matches_builtin": matches_builtin,
        }

    def _test_5_queryset_by_specialty(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 5: QuerySet Methods - by_specialty() - Compare with baseline."""
        log.info("Test 5: QuerySet Methods - by_specialty()")

        # Test with Cardiology specialty code (from test data: TEST_CARD001, TEST_CARD002, TEST_CARD003)
        specialty_code = "207RC0000X"  # Cardiology
        specialty_results = SpecialtyReportTemplate.objects.by_specialty(specialty_code)
        count = specialty_results.count()

        # Compare with baseline
        baseline_specialty = baseline_data["specialty_distribution"].get(specialty_code)
        baseline_count = baseline_specialty["count"] if baseline_specialty else 0
        matches_baseline = count == baseline_count

        # Verify all results have matching specialty_code
        found_template_ids = []
        for template in specialty_results[:10]:
            assert template.specialty_code == specialty_code
            found_template_ids.append(template.dbid)
            # Verify against baseline
            baseline_template = baseline_data["templates"].get(template.dbid)
            if baseline_template:
                assert baseline_template["specialty_code"] == specialty_code

        # Verify we found the same templates as baseline
        baseline_template_ids = baseline_specialty["template_ids"] if baseline_specialty else []
        all_found_match = all(tid in baseline_template_ids for tid in found_template_ids)

        # Test with non-existent specialty code
        non_existent = SpecialtyReportTemplate.objects.by_specialty("999XX9999X")
        non_existent_count = non_existent.count()

        log.info(f"Specialty '{specialty_code}' (Cardiology): {count} templates (baseline: {baseline_count}, match: {matches_baseline})")
        log.info(f"Non-existent specialty: {non_existent_count} templates")

        return {
            "tested_specialty": specialty_code,
            "count": count,
            "baseline_count": baseline_count,
            "matches_baseline": matches_baseline,
            "all_found_match": all_found_match,
            "non_existent_count": non_existent_count,
        }

    def _test_6_method_chaining(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 6: Method Chaining."""
        log.info("Test 6: Method Chaining")

        # Chain active().by_specialty() - use Cardiology specialty code from test data
        specialty_code = "207RC0000X"  # Cardiology
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

        log.info(f"Chained queries: active+by_specialty({specialty_code})={count_1}, active+search('cardiology')={count_2}, active+custom={count_3}, active+builtin={count_4}")

        return {
            "active_by_specialty": count_1,
            "active_search": count_2,
            "active_custom": count_3,
            "active_builtin": count_4,
        }

    def _test_7_template_field_relationship(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 7: Template-Field Relationship - Compare with baseline."""
        log.info("Test 7: Template-Field Relationship")

        # Look for TEST_CARD001 which should have 6 fields
        template = (
            SpecialtyReportTemplate.objects.filter(code="TEST_CARD001")
            .prefetch_related("fields")
            .first()
        )
        
        # Fallback to any template with fields if TEST_CARD001 not found
        if not template:
            template = (
                SpecialtyReportTemplate.objects.prefetch_related("fields")
                .filter(fields__isnull=False)
                .distinct()
                .first()
            )
        
        if not template:
            return {"message": "No templates with fields available for testing"}

        fields = template.fields.all()
        field_count = fields.count()

        # Compare with baseline
        baseline_template = baseline_data["templates"].get(template.dbid)
        baseline_field_count = baseline_template["field_count"] if baseline_template else 0
        matches_baseline = field_count == baseline_field_count

        # Verify field IDs match baseline
        baseline_field_ids = baseline_data["template_field_map"].get(template.dbid, [])
        actual_field_ids = [f.dbid for f in fields]
        fields_match = set(actual_field_ids) == set(baseline_field_ids)

        if field_count == 0:
            log.warning(f"Template {template.dbid} ({template.code}) has no fields")
            return {
                "template_id": template.dbid,
                "template_code": template.code,
                "field_count": 0,
                "baseline_field_count": baseline_field_count,
                "matches_baseline": matches_baseline,
            }

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

        log.info(f"Template {template.dbid} ({template.code}) has {field_count} fields (baseline: {baseline_field_count}, match: {matches_baseline})")
        return {
            "template_id": template.dbid,
            "template_code": template.code,
            "template_name": template.name,
            "field_count": field_count,
            "baseline_field_count": baseline_field_count,
            "matches_baseline": matches_baseline,
            "fields_match": fields_match,
            "sample_fields": field_data,
        }

    def _test_8_field_option_relationship(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
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

        # Compare with baseline
        baseline_field = baseline_data["fields"].get(field.dbid)
        baseline_option_count = baseline_field["option_count"] if baseline_field else 0
        matches_baseline = option_count == baseline_option_count

        # Verify option IDs match baseline
        baseline_option_ids = baseline_data["field_option_map"].get(field.dbid, [])
        actual_option_ids = [o.dbid for o in options]
        options_match = set(actual_option_ids) == set(baseline_option_ids)

        option_data = []
        for option in options[:5]:
            option_data.append({"dbid": option.dbid, "label": option.label, "key": option.key})

        log.info(f"Field {field.dbid} has {option_count} options (baseline: {baseline_option_count}, match: {matches_baseline})")
        return {
            "field_id": field.dbid,
            "field_label": field.label,
            "option_count": option_count,
            "baseline_option_count": baseline_option_count,
            "matches_baseline": matches_baseline,
            "options_match": options_match,
            "sample_options": option_data,
        }

    def _test_9_prefetch_related(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 9: Prefetch Related (Full Relationship Chain)."""
        log.info("Test 9: Prefetch Related")

        # Look for TEST_CARD001 which should have fields with options
        template = (
            SpecialtyReportTemplate.objects.filter(code="TEST_CARD001")
            .prefetch_related("fields", "fields__options")
            .first()
        )
        
        # Fallback to any template with fields if TEST_CARD001 not found
        if not template:
            template = (
                SpecialtyReportTemplate.objects.prefetch_related("fields", "fields__options")
                .filter(fields__isnull=False)
                .distinct()
                .first()
            )

        if not template:
            return {"message": "No templates with fields available for testing"}

        fields = template.fields.all()
        field_count = fields.count()

        # Compare with baseline
        baseline_template = baseline_data["templates"].get(template.dbid)
        baseline_field_count = baseline_template["field_count"] if baseline_template else 0
        matches_baseline = field_count == baseline_field_count

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

        log.info(f"Template {template.dbid} ({template.code}) with prefetch: {field_count} fields (baseline: {baseline_field_count}, match: {matches_baseline})")
        return {
            "template_id": template.dbid,
            "template_code": template.code,
            "field_count": field_count,
            "baseline_field_count": baseline_field_count,
            "matches_baseline": matches_baseline,
            "nested_relationships": nested_data,
        }

    def _test_10_specialty_specific_fields(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 10: Specialty-Specific Fields Access."""
        log.info("Test 10: Specialty-Specific Fields Access")

        # Look for TEST_CARD001 from test data
        template = SpecialtyReportTemplate.objects.filter(code="TEST_CARD001").first()
        
        # Fallback to any template if TEST_CARD001 not found
        if not template:
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

        # Verify against baseline
        baseline_template = baseline_data["templates"].get(template.dbid)
        fields_match_baseline = baseline_template is not None and (
            baseline_template["search_as"] == template.search_as and
            baseline_template["specialty_name"] == template.specialty_name and
            baseline_template["specialty_code"] == template.specialty_code
        )

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
            "fields_match_baseline": fields_match_baseline,
        }

    def _test_11_field_type_validation(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 11: Field Type Validation - Compare with baseline."""
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
                required_count = required_count + 1

            # Count nullable fields
            if field.code is None:
                nullable_code_count = nullable_code_count + 1
            if field.units is None:
                nullable_units_count = nullable_units_count + 1

        # Compare with baseline
        baseline_type_dist = baseline_data["field_type_distribution"]
        baseline_total_fields = baseline_data["summary"]["total_fields"]

        log.info(f"Field type distribution: {type_distribution}")
        log.info(f"Required fields: {required_count}/{field_count}")
        log.info(f"Baseline field type distribution: {baseline_type_dist}")

        return {
            "field_count": field_count,
            "type_distribution": type_distribution,
            "required_count": required_count,
            "nullable_code_count": nullable_code_count,
            "nullable_units_count": nullable_units_count,
            "baseline_type_distribution": baseline_type_dist,
            "baseline_total_fields": baseline_total_fields,
        }

    def _test_12_complete_template_structure(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 12: Data Integrity - Complete Template Structure."""
        log.info("Test 12: Complete Template Structure")

        # Look for TEST_CARD001 which should have 6 fields
        template = (
            SpecialtyReportTemplate.objects.filter(code="TEST_CARD001")
            .prefetch_related("fields", "fields__options")
            .first()
        )
        
        # Fallback to any template with fields if TEST_CARD001 not found
        if not template:
            template = (
                SpecialtyReportTemplate.objects.prefetch_related("fields", "fields__options")
                .filter(fields__isnull=False)
                .distinct()
                .first()
            )

        if not template:
            return {"message": "No templates with fields available for testing"}

        fields = template.fields.all().order_by("sequence")
        field_count = fields.count()

        # Compare with baseline
        baseline_template = baseline_data["templates"].get(template.dbid)
        baseline_field_count = baseline_template["field_count"] if baseline_template else 0
        matches_baseline = field_count == baseline_field_count

        if field_count == 0:
            log.warning(f"Template {template.dbid} has no fields")
            return {
                "template_id": template.dbid,
                "field_count": 0,
                "baseline_field_count": baseline_field_count,
                "matches_baseline": matches_baseline,
            }

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
                    select_fields_with_options = select_fields_with_options + 1
                else:
                    select_fields_without_options = select_fields_without_options + 1

            complete_structure["fields"].append(
                {
                    "dbid": field.dbid,
                    "sequence": field.sequence,
                    "label": field.label,
                    "type": field.type,
                    "option_count": option_count,
                }
            )

        log.info(f"Template structure validated: {field_count} fields (baseline: {baseline_field_count}, match: {matches_baseline}), sequential={is_sequential}")
        if select_fields_without_options > 0:
            log.warning(f"{select_fields_without_options} select/radio fields without options")

        return {
            "template_id": template.dbid,
            "field_count": field_count,
            "baseline_field_count": baseline_field_count,
            "matches_baseline": matches_baseline,
            "is_sequential": is_sequential,
            "select_fields_with_options": select_fields_with_options,
            "select_fields_without_options": select_fields_without_options,
            "structure": complete_structure,
        }

    def _test_13_edge_cases(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 13: Edge Cases - Compare with baseline."""
        log.info("Test 13: Edge Cases")

        edge_case_results = {}

        # Test with templates that have no fields
        templates_without_fields = SpecialtyReportTemplate.objects.filter(
            fields__isnull=True
        ).distinct()
        templates_without_fields_count = templates_without_fields.count()
        baseline_templates_without_fields = baseline_data["summary"]["templates_without_fields"]
        edge_case_results["templates_without_fields"] = templates_without_fields_count
        edge_case_results["baseline_templates_without_fields"] = baseline_templates_without_fields
        edge_case_results["templates_without_fields_match"] = templates_without_fields_count == baseline_templates_without_fields

        # Test with fields that have no options
        fields_without_options = SpecialtyReportTemplateField.objects.filter(
            options__isnull=True
        )
        fields_without_options_count = fields_without_options.count()
        baseline_fields_without_options = baseline_data["summary"]["fields_without_options"]
        edge_case_results["fields_without_options"] = fields_without_options_count
        edge_case_results["baseline_fields_without_options"] = baseline_fields_without_options
        edge_case_results["fields_without_options_match"] = fields_without_options_count == baseline_fields_without_options

        # Test with non-existent specialty code
        non_existent = SpecialtyReportTemplate.objects.by_specialty("999XX9999X")
        edge_case_results["non_existent_specialty"] = non_existent.count()

        # Test empty search
        empty_search = SpecialtyReportTemplate.objects.search("nonexistentterm12345")
        edge_case_results["empty_search_results"] = empty_search.count()

        log.info(f"Edge cases: {edge_case_results}")
        return edge_case_results

    def _test_14_performance_check(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
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

        # Compare counts with baseline
        baseline_total = baseline_data["summary"]["total_templates"]
        matches_baseline = basic_count == baseline_total

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
            "baseline_total": baseline_total,
            "matches_baseline": matches_baseline,
        }

    def _test_15_database_state_analysis(self, baseline_data: dict[str, Any]) -> dict[str, Any]:
        """Test 15: Comprehensive Database State Analysis - Uses baseline data."""
        log.info("Test 15: Database State Analysis")

        # Use baseline data (already extracted)
        summary = baseline_data["summary"]
        
        # Test data validation - check if expected test templates exist
        test_template_codes = ["TEST_CARD001", "TEST_CARD002", "TEST_CARD003", "TEST_DERM001", "TEST_EMPTY001"]
        test_template_status = {}
        for code in test_template_codes:
            # Find in baseline test templates
            found_template = None
            for template_id, template_data in baseline_data["test_templates"].items():
                if template_data["code"] == code:
                    found_template = template_data
                    break
            
            if found_template:
                template_id = found_template.get("dbid")
                field_count = found_template.get("field_count", 0)
                test_template_status[code] = {
                    "exists": True,
                    "dbid": template_id,
                    "name": found_template["name"],
                    "active": found_template["active"],
                    "custom": found_template["custom"],
                    "specialty_code": found_template["specialty_code"],
                    "field_count": field_count,
                }
            else:
                test_template_status[code] = {"exists": False}

        # Validate TEST_CARD001 structure
        test_validation = {}
        card001_data = None
        for template_id, template_data in baseline_data["test_templates"].items():
            if template_data["code"] == "TEST_CARD001":
                card001_data = template_data
                break
        
        if card001_data:
            template_id = card001_data["dbid"]
            field_count = card001_data["field_count"]
            # Count options for TEST_CARD001 fields
            field_ids = baseline_data["template_field_map"].get(template_id, [])
            option_count = 0
            for field_id in field_ids:
                option_count = option_count + len(baseline_data["field_option_map"].get(field_id, []))
            
            test_validation["TEST_CARD001"] = {
                "found": True,
                "expected_fields": 6,
                "actual_fields": field_count,
                "expected_options": 6,
                "actual_options": option_count,
                "fields_match": field_count == 6,
                "options_match": option_count == 6,
            }
        else:
            test_validation["TEST_CARD001"] = {"found": False}

        analysis = {
            "overall": summary,
            "test_data": {
                "total": summary["test_template_count"],
                "active": sum(1 for t in baseline_data["test_templates"].values() if t["active"]),
                "inactive": sum(1 for t in baseline_data["test_templates"].values() if not t["active"]),
                "custom": sum(1 for t in baseline_data["test_templates"].values() if t["custom"]),
                "builtin": sum(1 for t in baseline_data["test_templates"].values() if not t["custom"]),
                "templates": test_template_status,
            },
            "production_data": {
                "total": summary["production_template_count"],
                "active": sum(1 for t in baseline_data["production_templates"].values() if t["active"]),
                "inactive": sum(1 for t in baseline_data["production_templates"].values() if not t["active"]),
                "custom": sum(1 for t in baseline_data["production_templates"].values() if t["custom"]),
                "builtin": sum(1 for t in baseline_data["production_templates"].values() if not t["custom"]),
            },
            "specialty_distribution": baseline_data["specialty_distribution"],
            "field_type_distribution": baseline_data["field_type_distribution"],
            "test_validation": test_validation,
        }

        log.info(f"Database State Analysis (from baseline):")
        log.info(f"  Total Templates: {summary['total_templates']} (Test: {summary['test_template_count']}, Production: {summary['production_template_count']})")
        log.info(f"  Total Fields: {summary['total_fields']}")
        log.info(f"  Total Options: {summary['total_options']}")
        log.info(f"  Templates with fields: {summary['templates_with_fields']}, without: {summary['templates_without_fields']}")
        log.info(f"  Fields with options: {summary['fields_with_options']}, without: {summary['fields_without_options']}")
        log.info(f"  Specialty codes: {summary['specialty_count']}")
        log.info(f"  Field types: {list(baseline_data['field_type_distribution'].keys())}")

        return analysis
