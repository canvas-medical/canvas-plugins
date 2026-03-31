from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from django.db.transaction import atomic

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.v1.data import AttributeHub, CustomAttribute, Patient, Staff
from custom_data_uat.models.proxy import NoteProxy, PatientProxy, StaffProxy
from custom_data_uat.models.tag import PatientTag, Tag


class CustomDataUatAPI(StaffSessionAuthMixin, SimpleAPI):
    """UAT test suite for custom data features.

    Hit GET /run to execute all tests. Each section reports pass/fail
    with details. Cleans up after itself.
    """

    PREFIX = ""

    @api.get("/run")
    def run_all(self) -> list[Response | Effect]:
        """Run all UAT checks and return results as JSON."""
        results: dict[str, Any] = {}

        sections = [
            ("1_custom_model_crud", self._test_custom_model_crud),
            ("2_custom_model_relationships", self._test_custom_model_relationships),
            ("3_model_extension_proxy", self._test_model_extension_proxy),
            ("4_proxy_field", self._test_proxy_field),
            ("5_attribute_hub_crud", self._test_attribute_hub_crud),
            ("6_attribute_hub_typed_values", self._test_attribute_hub_typed_values),
            ("7_attribute_hub_filtering", self._test_attribute_hub_filtering),
            ("8_attribute_hub_with_only", self._test_attribute_hub_with_only),
            ("9_attribute_hub_bulk", self._test_attribute_hub_bulk),
            ("10_transactions", self._test_transactions),
        ]

        for name, fn in sections:
            try:
                results[name] = fn()
            except Exception as e:
                results[name] = {"passed": False, "error": f"{e.__class__.__name__}: {e}"}

        all_passed = all(
            section.get("passed", False)
            for section in results.values()
            if isinstance(section, dict)
        )
        results["all_passed"] = all_passed

        return [JSONResponse(results)]

    # ------------------------------------------------------------------
    # 1. CustomModel CRUD
    # ------------------------------------------------------------------

    def _test_custom_model_crud(self) -> dict:
        """Create, read, update, delete a Tag."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        # Create
        tag = Tag.objects.create(label="uat-test", color="blue")
        section["checks"]["create_dbid"] = tag.dbid
        section["checks"]["create_label"] = tag.label
        section["checks"]["create_color"] = tag.color

        # Read
        fetched = Tag.objects.get(dbid=tag.dbid)
        section["checks"]["read_matches"] = fetched.label == "uat-test"

        # Update
        fetched.color = "red"
        fetched.save()
        refreshed = Tag.objects.get(dbid=tag.dbid)
        section["checks"]["update_color"] = refreshed.color

        # Delete
        tag_dbid = tag.dbid
        tag.delete()
        exists = Tag.objects.filter(dbid=tag_dbid).exists()
        section["checks"]["deleted"] = not exists

        section["passed"] = (
            section["checks"]["read_matches"]
            and section["checks"]["update_color"] == "red"
            and section["checks"]["deleted"]
        )
        return section

    # ------------------------------------------------------------------
    # 2. CustomModel relationships (FK, UniqueConstraint, cascade)
    # ------------------------------------------------------------------

    def _test_custom_model_relationships(self) -> dict:
        """Test FK relationships, UniqueConstraint, and cascade delete."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        patient = PatientProxy.objects.first()
        if not patient:
            section["checks"]["note"] = "No patients found — cannot test"
            section["passed"] = True
            return section

        # Create tag + patient_tag
        tag = Tag.objects.create(label="uat-rel-test", color="green")
        pt = PatientTag.objects.create(tag=tag, patient=patient, priority=1)
        section["checks"]["patient_tag_dbid"] = pt.dbid

        # FK traversal
        section["checks"]["tag_via_fk"] = pt.tag.label == "uat-rel-test"

        # Reverse relation
        tags_for_tag = PatientTag.objects.filter(tag=tag)
        section["checks"]["reverse_count"] = tags_for_tag.count()

        # UniqueConstraint violation
        duplicate_ok = False
        try:
            PatientTag.objects.create(tag=tag, patient=patient, priority=2)
        except Exception:
            duplicate_ok = True
        section["checks"]["unique_constraint_enforced"] = duplicate_ok

        # select_related
        pt_sr = PatientTag.objects.select_related("tag").get(dbid=pt.dbid)
        section["checks"]["select_related_label"] = pt_sr.tag.label

        # Cascade delete: deleting tag should delete patient_tag
        pt_dbid = pt.dbid
        tag.delete()
        section["checks"]["cascade_deleted"] = not PatientTag.objects.filter(dbid=pt_dbid).exists()

        section["passed"] = (
            section["checks"]["tag_via_fk"]
            and section["checks"]["reverse_count"] == 1
            and section["checks"]["unique_constraint_enforced"]
            and section["checks"]["select_related_label"] == "uat-rel-test"
            and section["checks"]["cascade_deleted"]
        )
        return section

    # ------------------------------------------------------------------
    # 3. ModelExtension proxy
    # ------------------------------------------------------------------

    def _test_model_extension_proxy(self) -> dict:
        """Test that ModelExtension proxies add computed properties."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        staff = StaffProxy.objects.first()
        if not staff:
            section["checks"]["note"] = "No staff found"
            section["passed"] = True
            return section

        section["checks"]["has_display_name"] = hasattr(staff, "display_name")
        section["checks"]["display_name"] = staff.display_name
        section["checks"]["is_staff_proxy"] = isinstance(staff, StaffProxy)
        section["checks"]["is_staff_subclass"] = isinstance(staff, Staff)

        patient = PatientProxy.objects.first()
        if patient:
            section["checks"]["patient_display_name"] = patient.display_name
            section["checks"]["is_patient_proxy"] = isinstance(patient, PatientProxy)
            section["checks"]["is_patient_subclass"] = isinstance(patient, Patient)

        section["passed"] = (
            section["checks"]["has_display_name"]
            and bool(section["checks"]["display_name"])
            and section["checks"]["is_staff_proxy"]
            and section["checks"]["is_staff_subclass"]
        )
        return section

    # ------------------------------------------------------------------
    # 4. proxy_field
    # ------------------------------------------------------------------

    def _test_proxy_field(self) -> dict:
        """Test that proxy_field makes FK traversal return proxy instances."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        note = (
            NoteProxy.objects.select_related("patient", "provider")
            .filter(patient__isnull=False, provider__isnull=False)
            .first()
        )
        if not note:
            section["checks"]["note"] = "No notes with patient+provider found"
            section["passed"] = True
            return section

        section["checks"]["note_dbid"] = note.dbid
        section["checks"]["patient_type"] = note.patient.__class__.__name__
        section["checks"]["patient_is_proxy"] = isinstance(note.patient, PatientProxy)
        section["checks"]["patient_display_name"] = note.patient.display_name

        section["checks"]["provider_type"] = note.provider.__class__.__name__
        section["checks"]["provider_is_proxy"] = isinstance(note.provider, StaffProxy)
        section["checks"]["provider_display_name"] = note.provider.display_name

        section["passed"] = (
            section["checks"]["patient_is_proxy"]
            and section["checks"]["provider_is_proxy"]
            and bool(section["checks"]["patient_display_name"])
            and bool(section["checks"]["provider_display_name"])
        )
        return section

    # ------------------------------------------------------------------
    # 5. AttributeHub CRUD
    # ------------------------------------------------------------------

    def _test_attribute_hub_crud(self) -> dict:
        """Create hub, set/get/delete attributes."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        # Create hub
        hub = AttributeHub.objects.create(type="uat", id="test-crud-1")
        section["checks"]["hub_dbid"] = hub.dbid

        # set_attribute
        hub.set_attribute("color", "blue")
        section["checks"]["get_color"] = hub.get_attribute("color")

        # Update attribute
        hub.set_attribute("color", "red")
        section["checks"]["updated_color"] = hub.get_attribute("color")

        # get_attribute on missing key
        section["checks"]["missing_attr"] = hub.get_attribute("nonexistent")

        # delete_attribute
        deleted = hub.delete_attribute("color")
        section["checks"]["delete_returned_true"] = deleted
        section["checks"]["after_delete"] = hub.get_attribute("color")

        # delete non-existent
        section["checks"]["delete_missing_returned_false"] = not hub.delete_attribute("nope")

        # Cleanup
        hub.delete()

        section["passed"] = (
            section["checks"]["get_color"] == "blue"
            and section["checks"]["updated_color"] == "red"
            and section["checks"]["missing_attr"] is None
            and section["checks"]["delete_returned_true"]
            and section["checks"]["after_delete"] is None
            and section["checks"]["delete_missing_returned_false"]
        )
        return section

    # ------------------------------------------------------------------
    # 6. AttributeHub typed values
    # ------------------------------------------------------------------

    def _test_attribute_hub_typed_values(self) -> dict:
        """Test that all value types round-trip correctly."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        hub = AttributeHub.objects.create(type="uat", id="test-types-1")

        test_values: dict[str, Any] = {
            "text_val": "hello world",
            "int_val": 42,
            "bool_true": True,
            "bool_false": False,
            "decimal_val": Decimal("3.1415926535"),
            "date_val": date(2026, 3, 24),
            "datetime_val": datetime(2026, 3, 24, 15, 30, 0, tzinfo=UTC),
            "json_dict": {"key": "value", "nested": [1, 2, 3]},
            "json_list": [1, "two", 3.0],
        }

        for name, value in test_values.items():
            hub.set_attribute(name, value)

        all_match = True
        for name, expected in test_values.items():
            actual = hub.get_attribute(name)
            # Decimal comes back from DB — compare string repr
            if isinstance(expected, (Decimal, date, datetime)):
                match = str(actual) == str(expected)
            else:
                match = actual == expected
            section["checks"][name] = {
                "expected": str(expected),
                "actual": str(actual),
                "match": match,
            }
            if not match:
                all_match = False

        # Also test None value
        hub.set_attribute("null_val", None)
        null_result = hub.get_attribute("null_val")
        section["checks"]["null_val"] = {
            "expected": "None",
            "actual": str(null_result),
            "match": null_result is None,
        }
        if null_result is not None:
            all_match = False

        hub.delete()
        section["passed"] = all_match
        return section

    # ------------------------------------------------------------------
    # 7. AttributeHub filtering by value
    # ------------------------------------------------------------------

    def _test_attribute_hub_filtering(self) -> dict:
        """Test CustomAttribute queryset value-type rewriting."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        hub = AttributeHub.objects.create(type="uat", id="test-filter-1")
        hub.set_attribute("score", 100)
        hub.set_attribute("name", "alice")
        hub.set_attribute("active", True)

        # Filter by text value
        text_attrs = CustomAttribute.objects.filter(hub=hub, value="alice")
        section["checks"]["filter_text_count"] = text_attrs.count()

        # Filter by int value with gte
        int_attrs = CustomAttribute.objects.filter(hub=hub, value__gte=50)
        section["checks"]["filter_int_gte_count"] = int_attrs.count()

        # Filter by bool value
        bool_attrs = CustomAttribute.objects.filter(hub=hub, value=True)
        section["checks"]["filter_bool_count"] = bool_attrs.count()

        # Filter via cross-relation (hub → custom_attributes__value)
        hubs = AttributeHub.objects.filter(
            type="uat",
            id="test-filter-1",
            custom_attributes__value="alice",
        )
        section["checks"]["cross_relation_filter_count"] = hubs.count()

        # value=None filter (all columns NULL)
        hub.set_attribute("empty", None)
        null_attrs = CustomAttribute.objects.filter(hub=hub, value=None)
        section["checks"]["filter_null_count"] = null_attrs.count()

        # value__isnull=False
        non_null_attrs = CustomAttribute.objects.filter(hub=hub, value__isnull=False)
        section["checks"]["filter_non_null_count"] = non_null_attrs.count()

        hub.delete()

        section["passed"] = (
            section["checks"]["filter_text_count"] == 1
            and section["checks"]["filter_int_gte_count"] == 1
            and section["checks"]["filter_bool_count"] == 1
            and section["checks"]["cross_relation_filter_count"] == 1
            and section["checks"]["filter_null_count"] == 1
            and section["checks"]["filter_non_null_count"] == 3
        )
        return section

    # ------------------------------------------------------------------
    # 8. AttributeHub with_only (selective prefetch)
    # ------------------------------------------------------------------

    def _test_attribute_hub_with_only(self) -> dict:
        """Test with_only() selective prefetching."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        hub = AttributeHub.objects.create(type="uat", id="test-with-only-1")
        hub.set_attribute("color", "blue")
        hub.set_attribute("size", "large")
        hub.set_attribute("weight", 42)

        # Prefetch only "color"
        hub_limited = AttributeHub.objects.with_only("color").get(dbid=hub.dbid)
        prefetched_attrs = list(hub_limited.custom_attributes.all())
        section["checks"]["prefetched_count"] = len(prefetched_attrs)
        section["checks"]["prefetched_name"] = (
            prefetched_attrs[0].name if prefetched_attrs else None
        )

        # get_attribute falls back to DB for non-prefetched attrs
        section["checks"]["color_from_prefetch"] = hub_limited.get_attribute("color")
        section["checks"]["size_from_fallback"] = hub_limited.get_attribute("size")

        # Prefetch multiple
        hub_multi = AttributeHub.objects.with_only(["color", "size"]).get(dbid=hub.dbid)
        multi_attrs = list(hub_multi.custom_attributes.all())
        section["checks"]["multi_prefetched_count"] = len(multi_attrs)

        hub.delete()

        section["passed"] = (
            section["checks"]["prefetched_count"] == 1
            and section["checks"]["prefetched_name"] == "color"
            and section["checks"]["color_from_prefetch"] == "blue"
            and section["checks"]["size_from_fallback"] == "large"
            and section["checks"]["multi_prefetched_count"] == 2
        )
        return section

    # ------------------------------------------------------------------
    # 9. AttributeHub bulk operations
    # ------------------------------------------------------------------

    def _test_attribute_hub_bulk(self) -> dict:
        """Test set_attributes (bulk) and verify results."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        hub = AttributeHub.objects.create(type="uat", id="test-bulk-1")

        # Bulk set
        attrs = hub.set_attributes(
            {
                "a": "alpha",
                "b": 2,
                "c": True,
                "d": {"nested": "json"},
            }
        )
        section["checks"]["bulk_created_count"] = len(attrs)

        # Verify all set
        section["checks"]["a"] = hub.get_attribute("a")
        section["checks"]["b"] = hub.get_attribute("b")
        section["checks"]["c"] = hub.get_attribute("c")
        section["checks"]["d"] = hub.get_attribute("d")

        # Bulk upsert (update existing + add new)
        hub.set_attributes({"a": "ALPHA", "e": "echo"})
        section["checks"]["a_updated"] = hub.get_attribute("a")
        section["checks"]["e_added"] = hub.get_attribute("e")

        # Total attribute count
        total = CustomAttribute.objects.filter(hub=hub).count()
        section["checks"]["total_attrs"] = total

        hub.delete()

        section["passed"] = (
            section["checks"]["bulk_created_count"] == 4
            and section["checks"]["a"] == "alpha"
            and section["checks"]["b"] == 2
            and section["checks"]["c"] is True
            and section["checks"]["d"] == {"nested": "json"}
            and section["checks"]["a_updated"] == "ALPHA"
            and section["checks"]["e_added"] == "echo"
            and section["checks"]["total_attrs"] == 5
        )
        return section

    # ------------------------------------------------------------------
    # 10. Transactions (atomic multi-model writes)
    # ------------------------------------------------------------------

    def _test_transactions(self) -> dict:
        """Test atomic() rollback and commit across CustomModels."""
        section: dict[str, Any] = {"passed": False, "checks": {}}

        patient = PatientProxy.objects.first()
        if not patient:
            section["checks"]["note"] = "No patients found — cannot test"
            section["passed"] = True
            return section

        # Test 1: Successful atomic block commits both tag and patient_tag
        tag = None
        try:
            with atomic():
                tag = Tag.objects.create(label="uat-txn-commit", color="green")
                PatientTag.objects.create(tag=tag, patient=patient, priority=5)
        except Exception as e:
            section["checks"]["commit_error"] = str(e)

        if tag:
            section["checks"]["commit_tag_exists"] = Tag.objects.filter(dbid=tag.dbid).exists()
            section["checks"]["commit_pt_exists"] = PatientTag.objects.filter(tag=tag).exists()

        # Test 2: Failed atomic block rolls back everything
        rollback_tag_label = "uat-txn-rollback"
        try:
            with atomic():
                Tag.objects.create(label=rollback_tag_label, color="red")
                # Force an error — duplicate UniqueConstraint violation
                PatientTag.objects.create(tag=tag, patient=patient, priority=1)
                PatientTag.objects.create(tag=tag, patient=patient, priority=2)
        except Exception:
            pass  # Expected — IntegrityError from UniqueConstraint violation

        section["checks"]["rollback_tag_gone"] = not Tag.objects.filter(
            label=rollback_tag_label
        ).exists()

        # Test 3: Nested savepoint — inner failure doesn't kill outer
        outer_tag = None
        try:
            with atomic():
                outer_tag = Tag.objects.create(label="uat-txn-outer", color="blue")
                try:
                    with atomic():
                        Tag.objects.create(label="uat-txn-inner", color="purple")
                        raise ValueError("deliberate inner failure")
                except ValueError:
                    pass  # Inner savepoint rolled back
                # Outer should still commit
        except Exception as e:
            section["checks"]["nested_error"] = str(e)

        if outer_tag:
            section["checks"]["outer_survived"] = Tag.objects.filter(dbid=outer_tag.dbid).exists()
            section["checks"]["inner_rolled_back"] = not Tag.objects.filter(
                label="uat-txn-inner"
            ).exists()

        # Cleanup
        if tag:
            tag.delete()
        if outer_tag:
            outer_tag.delete()

        section["passed"] = (
            section["checks"].get("commit_tag_exists", False)
            and section["checks"].get("commit_pt_exists", False)
            and section["checks"].get("rollback_tag_gone", False)
            and section["checks"].get("outer_survived", False)
            and section["checks"].get("inner_rolled_back", False)
        )
        return section
