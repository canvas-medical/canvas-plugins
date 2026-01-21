"""Tests for CustomAttribute value setter and getter.

Tests verify that:
1. The setter correctly determines the data type and stores in the appropriate field
2. The getter returns the correct value from the appropriate field
3. Edge cases like bool vs int and datetime vs date are handled correctly
4. CustomAttributeMixinMetaClass sets app_label correctly for proxy classes
"""

import datetime
import decimal

import pytest

from canvas_sdk.v1.data.custom_attribute import (
    CustomAttribute,
    CustomAttributeMixin,
    CustomAttributeMixinMetaClass,
)


class TestCustomAttributeValueSetter:
    """Tests for the CustomAttribute.value setter."""

    @pytest.fixture
    def attr(self):
        """Create a fresh CustomAttribute instance for each test."""
        return CustomAttribute(name="test_attr")

    # -------------------------------------------------------------------------
    # String values
    # -------------------------------------------------------------------------

    def test_string_value_stored_in_text_value(self, attr):
        attr.value = "hello world"

        assert attr.text_value == "hello world"
        assert attr.int_value is None
        assert attr.bool_value is None
        assert attr.decimal_value is None
        assert attr.timestamp_value is None
        assert attr.date_value is None
        assert attr.json_value is None

    def test_empty_string_stored_in_text_value(self, attr):
        attr.value = ""

        assert attr.text_value == ""

    def test_unicode_string_stored_in_text_value(self, attr):
        attr.value = "こんにちは世界 🌍"

        assert attr.text_value == "こんにちは世界 🌍"

    # -------------------------------------------------------------------------
    # Integer values
    # -------------------------------------------------------------------------

    def test_positive_int_stored_in_int_value(self, attr):
        attr.value = 42

        assert attr.int_value == 42
        assert attr.text_value is None
        assert attr.bool_value is None
        assert attr.decimal_value is None
        assert attr.timestamp_value is None
        assert attr.date_value is None
        assert attr.json_value is None

    def test_negative_int_stored_in_int_value(self, attr):
        attr.value = -100

        assert attr.int_value == -100

    def test_zero_stored_in_int_value(self, attr):
        attr.value = 0

        assert attr.int_value == 0

    def test_large_int_stored_in_int_value(self, attr):
        attr.value = 2**31 - 1  # Max 32-bit signed int

        assert attr.int_value == 2**31 - 1

    # -------------------------------------------------------------------------
    # Boolean values - CRITICAL: bool is subclass of int in Python
    # -------------------------------------------------------------------------

    def test_true_stored_in_bool_value_not_int(self, attr):
        """True should go to bool_value, not int_value (even though bool is subclass of int)."""
        attr.value = True

        assert attr.bool_value is True
        assert attr.int_value is None  # NOT 1

    def test_false_stored_in_bool_value_not_int(self, attr):
        """False should go to bool_value, not int_value (even though bool is subclass of int)."""
        attr.value = False

        assert attr.bool_value is False
        assert attr.int_value is None  # NOT 0

    # -------------------------------------------------------------------------
    # Float values
    # -------------------------------------------------------------------------

    def test_float_stored_in_decimal_value(self, attr):
        attr.value = 3.14159

        assert attr.decimal_value == 3.14159
        assert attr.int_value is None
        assert attr.text_value is None

    def test_negative_float_stored_in_decimal_value(self, attr):
        attr.value = -273.15

        assert attr.decimal_value == -273.15

    def test_float_zero_stored_in_decimal_value(self, attr):
        attr.value = 0.0

        assert attr.decimal_value == 0.0

    # -------------------------------------------------------------------------
    # Decimal values
    # -------------------------------------------------------------------------

    def test_decimal_stored_in_decimal_value(self, attr):
        attr.value = decimal.Decimal("123.456789")

        assert attr.decimal_value == decimal.Decimal("123.456789")

    def test_decimal_high_precision_stored_in_decimal_value(self, attr):
        attr.value = decimal.Decimal("0.0000000001")

        assert attr.decimal_value == decimal.Decimal("0.0000000001")

    # -------------------------------------------------------------------------
    # Datetime values - CRITICAL: datetime is subclass of date in Python
    # -------------------------------------------------------------------------

    def test_datetime_stored_in_timestamp_value_not_date(self, attr):
        """Datetime should go to timestamp_value, not date_value."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45)
        attr.value = dt

        assert attr.timestamp_value == dt
        assert attr.date_value is None  # NOT the date part

    def test_datetime_with_timezone_stored_in_timestamp_value(self, attr):
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45, tzinfo=datetime.UTC)
        attr.value = dt

        assert attr.timestamp_value == dt

    def test_datetime_with_microseconds_stored_in_timestamp_value(self, attr):
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45, 123456)
        attr.value = dt

        assert attr.timestamp_value == dt

    # -------------------------------------------------------------------------
    # Date values
    # -------------------------------------------------------------------------

    def test_date_stored_in_date_value(self, attr):
        d = datetime.date(2024, 1, 15)
        attr.value = d

        assert attr.date_value == d
        assert attr.timestamp_value is None

    # -------------------------------------------------------------------------
    # None value
    # -------------------------------------------------------------------------

    def test_none_clears_all_fields(self, attr):
        # First set a value
        attr.value = "test"
        assert attr.text_value == "test"

        # Then set to None
        attr.value = None

        assert attr.text_value is None
        assert attr.int_value is None
        assert attr.bool_value is None
        assert attr.decimal_value is None
        assert attr.timestamp_value is None
        assert attr.date_value is None
        assert attr.json_value is None

    # -------------------------------------------------------------------------
    # JSON/complex values
    # -------------------------------------------------------------------------

    def test_dict_stored_in_json_value(self, attr):
        data = {"key": "value", "nested": {"a": 1}}
        attr.value = data

        assert attr.json_value == data
        assert attr.text_value is None

    def test_list_stored_in_json_value(self, attr):
        data = [1, 2, 3, "four", {"five": 5}]
        attr.value = data

        assert attr.json_value == data

    def test_empty_dict_stored_in_json_value(self, attr):
        attr.value = {}

        assert attr.json_value == {}

    def test_empty_list_stored_in_json_value(self, attr):
        attr.value = []

        assert attr.json_value == []

    # -------------------------------------------------------------------------
    # Value replacement clears previous field
    # -------------------------------------------------------------------------

    def test_changing_type_clears_previous_field(self, attr):
        """Setting a new value type should clear the old field."""
        attr.value = "string"
        assert attr.text_value == "string"

        attr.value = 42
        assert attr.int_value == 42
        assert attr.text_value is None  # Should be cleared

    def test_multiple_type_changes(self, attr):
        """Test cycling through multiple types."""
        attr.value = "text"
        assert attr.text_value == "text"

        attr.value = 123
        assert attr.int_value == 123
        assert attr.text_value is None

        attr.value = True
        assert attr.bool_value is True
        assert attr.int_value is None

        attr.value = {"json": True}
        assert attr.json_value == {"json": True}
        assert attr.bool_value is None


class TestCustomAttributeValueGetter:
    """Tests for the CustomAttribute.value getter."""

    @pytest.fixture
    def attr(self):
        """Create a fresh CustomAttribute instance for each test."""
        return CustomAttribute(name="test_attr")

    # -------------------------------------------------------------------------
    # Get values from each field type
    # -------------------------------------------------------------------------

    def test_get_text_value(self, attr):
        attr.text_value = "hello"

        assert attr.value == "hello"

    def test_get_int_value(self, attr):
        attr.int_value = 42

        assert attr.value == 42

    def test_get_bool_value_true(self, attr):
        attr.bool_value = True

        assert attr.value is True

    def test_get_bool_value_false(self, attr):
        attr.bool_value = False

        assert attr.value is False

    def test_get_decimal_value(self, attr):
        attr.decimal_value = decimal.Decimal("3.14")

        assert attr.value == decimal.Decimal("3.14")

    def test_get_timestamp_value(self, attr):
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45)
        attr.timestamp_value = dt

        assert attr.value == dt

    def test_get_date_value(self, attr):
        d = datetime.date(2024, 1, 15)
        attr.date_value = d

        assert attr.value == d

    def test_get_json_value_dict(self, attr):
        attr.json_value = {"key": "value"}

        assert attr.value == {"key": "value"}

    def test_get_json_value_list(self, attr):
        attr.json_value = [1, 2, 3]

        assert attr.value == [1, 2, 3]

    # -------------------------------------------------------------------------
    # Get None when no value is set
    # -------------------------------------------------------------------------

    def test_get_returns_none_when_all_fields_empty(self, attr):
        assert attr.value is None

    # -------------------------------------------------------------------------
    # Round-trip tests (set then get)
    # -------------------------------------------------------------------------

    def test_roundtrip_string(self, attr):
        attr.value = "test string"
        assert attr.value == "test string"

    def test_roundtrip_int(self, attr):
        attr.value = 12345
        assert attr.value == 12345

    def test_roundtrip_bool_true(self, attr):
        attr.value = True
        assert attr.value is True

    def test_roundtrip_bool_false(self, attr):
        attr.value = False
        assert attr.value is False

    def test_roundtrip_float(self, attr):
        attr.value = 3.14159
        assert attr.value == 3.14159

    def test_roundtrip_decimal(self, attr):
        attr.value = decimal.Decimal("999.99")
        assert attr.value == decimal.Decimal("999.99")

    def test_roundtrip_datetime(self, attr):
        dt = datetime.datetime(2024, 6, 15, 14, 30, 0)
        attr.value = dt
        assert attr.value == dt

    def test_roundtrip_date(self, attr):
        d = datetime.date(2024, 6, 15)
        attr.value = d
        assert attr.value == d

    def test_roundtrip_dict(self, attr):
        data = {"nested": {"data": [1, 2, 3]}}
        attr.value = data
        assert attr.value == data

    def test_roundtrip_list(self, attr):
        data = ["a", "b", "c"]
        attr.value = data
        assert attr.value == data

    def test_roundtrip_none(self, attr):
        attr.value = "something"
        attr.value = None
        assert attr.value is None


class TestCustomAttributeValueTypeDiscrimination:
    """Tests specifically for type discrimination edge cases.

    Python has inheritance relationships that can cause issues:
    - bool is a subclass of int (True == 1, False == 0)
    - datetime is a subclass of date

    Using isinstance() would incorrectly categorize these.
    Using type() ensures exact type matching.
    """

    @pytest.fixture
    def attr(self):
        return CustomAttribute(name="test_attr")

    def test_bool_true_is_not_stored_as_int_1(self, attr):
        """Verify True goes to bool_value, not int_value as 1."""
        attr.value = True

        # Should be in bool_value
        assert attr.bool_value is True
        # Should NOT be in int_value
        assert attr.int_value is None

        # Verify the getter returns a bool, not int
        retrieved = attr.value
        assert retrieved is True
        assert type(retrieved) is bool

    def test_bool_false_is_not_stored_as_int_0(self, attr):
        """Verify False goes to bool_value, not int_value as 0."""
        attr.value = False

        assert attr.bool_value is False
        assert attr.int_value is None

        retrieved = attr.value
        assert retrieved is False
        assert type(retrieved) is bool

    def test_int_1_is_not_stored_as_bool_true(self, attr):
        """Verify 1 goes to int_value, not bool_value as True."""
        attr.value = 1

        assert attr.int_value == 1
        assert attr.bool_value is None

        retrieved = attr.value
        assert retrieved == 1
        assert type(retrieved) is int

    def test_int_0_is_not_stored_as_bool_false(self, attr):
        """Verify 0 goes to int_value, not bool_value as False."""
        attr.value = 0

        assert attr.int_value == 0
        assert attr.bool_value is None

        retrieved = attr.value
        assert retrieved == 0
        assert type(retrieved) is int

    def test_datetime_is_not_stored_as_date(self, attr):
        """Verify datetime goes to timestamp_value, not date_value."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45)
        attr.value = dt

        assert attr.timestamp_value == dt
        assert attr.date_value is None

        retrieved = attr.value
        assert retrieved == dt
        assert type(retrieved) is datetime.datetime

    def test_date_is_stored_as_date_not_datetime(self, attr):
        """Verify date goes to date_value, not timestamp_value."""
        d = datetime.date(2024, 1, 15)
        attr.value = d

        assert attr.date_value == d
        assert attr.timestamp_value is None

        # Note: The getter will return the date value
        retrieved = attr.value
        assert retrieved == d

    def test_float_is_not_confused_with_int(self, attr):
        """Verify float goes to decimal_value, not int_value."""
        attr.value = 1.0  # This is a float, even though it equals int 1

        assert attr.decimal_value == 1.0
        assert attr.int_value is None

    def test_decimal_is_not_confused_with_float(self, attr):
        """Verify Decimal goes to decimal_value alongside float."""
        attr.value = decimal.Decimal("1.0")

        assert attr.decimal_value == decimal.Decimal("1.0")
        assert attr.int_value is None


class TestCustomAttributeValueGetterPriority:
    """Tests for the getter's field priority when multiple fields have values.

    In normal operation, only one field should have a value at a time.
    These tests verify the getter's behavior if somehow multiple fields
    are populated (e.g., direct field assignment without using setter).
    """

    @pytest.fixture
    def attr(self):
        return CustomAttribute(name="test_attr")

    def test_text_value_has_priority(self, attr):
        """text_value is checked first in the getter."""
        attr.text_value = "text"
        attr.int_value = 42

        assert attr.value == "text"

    def test_date_value_before_timestamp_value(self, attr):
        """date_value is checked before timestamp_value."""
        attr.date_value = datetime.date(2024, 1, 1)
        attr.timestamp_value = datetime.datetime(2024, 6, 15, 10, 0, 0)

        assert attr.value == datetime.date(2024, 1, 1)

    def test_int_value_before_decimal_value(self, attr):
        """int_value is checked before decimal_value."""
        attr.int_value = 42
        attr.decimal_value = decimal.Decimal("3.14")

        assert attr.value == 42


# ===========================================================================
# Tests for CustomAttributeMixinMetaClass app_label behavior
# ===========================================================================


class TestCustomAttributeMixinMetaClassAppLabel:
    """Tests that CustomAttributeMixinMetaClass sets app_label correctly.

    The metaclass sets app_label based on __module__:
    - If __module__ starts with "canvas_sdk", app_label is NOT set by metaclass
    - If __module__ does NOT start with "canvas_sdk" (e.g., a plugin),
      app_label is set to the first part of the module name
    """

    def test_plugin_module_gets_app_label_from_module_name(self):
        """Classes in plugin modules should get app_label from first module part."""
        # Simulate a class defined in "my_plugin.models.custom"
        attrs = {
            "__module__": "my_plugin.models.custom",
            "__qualname__": "MyPluginModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        # The metaclass should set app_label to "my_plugin"
        meta = attrs["Meta"]
        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "MyPluginModel",
            (CustomAttributeMixin,),
            attrs,
        )

        assert meta.app_label == "my_plugin"

    def test_deeply_nested_plugin_module_gets_first_part(self):
        """Deeply nested modules should still get first part as app_label."""
        attrs = {
            "__module__": "awesome_plugin.sub.models.deeply.nested",
            "__qualname__": "DeepModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta = attrs["Meta"]
        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "DeepModel",
            (CustomAttributeMixin,),
            attrs,
        )

        assert meta.app_label == "awesome_plugin"

    def test_canvas_sdk_module_does_not_override_app_label(self):
        """Classes in canvas_sdk modules should NOT have app_label set by metaclass."""
        attrs = {
            "__module__": "canvas_sdk.v1.data.custom_attribute",
            "__qualname__": "SdkModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta = attrs["Meta"]
        # Ensure app_label is not set initially
        assert not hasattr(meta, "app_label")

        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "SdkModel",
            (CustomAttributeMixin,),
            attrs,
        )

        # app_label should NOT be set by the metaclass for canvas_sdk modules
        assert not hasattr(meta, "app_label")

    def test_canvas_sdk_submodule_does_not_override_app_label(self):
        """Any canvas_sdk.* module should not have app_label overridden."""
        attrs = {
            "__module__": "canvas_sdk.effects.something",
            "__qualname__": "EffectModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta = attrs["Meta"]
        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "EffectModel",
            (CustomAttributeMixin,),
            attrs,
        )

        assert not hasattr(meta, "app_label")

    def test_single_word_module_name(self):
        """Single word module names should work (edge case)."""
        attrs = {
            "__module__": "myplugin",
            "__qualname__": "SimpleModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta = attrs["Meta"]
        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "SimpleModel",
            (CustomAttributeMixin,),
            attrs,
        )

        assert meta.app_label == "myplugin"

    def test_meta_class_created_if_not_provided(self):
        """If Meta is not provided, it should be created and app_label set."""
        attrs = {
            "__module__": "test_plugin.models",
            "__qualname__": "NoMetaModel",
            # No Meta class provided
        }

        new_class = CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "NoMetaModel",
            (CustomAttributeMixin,),
            attrs,
        )

        # The created class should have app_label set correctly
        assert new_class._meta.app_label == "test_plugin"

    def test_existing_app_label_overwritten_for_plugins(self):
        """Existing app_label should be overwritten for plugin modules."""
        attrs = {
            "__module__": "new_plugin.models",
            "__qualname__": "OverwriteModel",
            "Meta": type("Meta", (), {"abstract": True, "app_label": "old_label"}),
        }

        meta = attrs["Meta"]
        assert meta.app_label == "old_label"

        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "OverwriteModel",
            (CustomAttributeMixin,),
            attrs,
        )

        # Should be overwritten to match module
        assert meta.app_label == "new_plugin"

    def test_hyphenated_plugin_name(self):
        """Plugin names with hyphens should work."""
        attrs = {
            "__module__": "my-cool-plugin.models",
            "__qualname__": "HyphenModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta = attrs["Meta"]
        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "HyphenModel",
            (CustomAttributeMixin,),
            attrs,
        )

        assert meta.app_label == "my-cool-plugin"

    def test_underscored_plugin_name(self):
        """Plugin names with underscores should work."""
        attrs = {
            "__module__": "my_cool_plugin.models.data",
            "__qualname__": "UnderscoreModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta = attrs["Meta"]
        CustomAttributeMixinMetaClass.__new__(
            CustomAttributeMixinMetaClass,
            "UnderscoreModel",
            (CustomAttributeMixin,),
            attrs,
        )

        assert meta.app_label == "my_cool_plugin"


# ===========================================================================
# Tests for set_attributes bulk operation logic
# ===========================================================================


@pytest.mark.django_db
class TestSetAttributesBulkOperations:
    """Tests for CustomAttributeMixin.set_attributes method.

    Tests cover the three main scenarios:
    1. All new attributes (bulk_create only)
    2. All existing attributes to update (bulk_update only)
    3. Mixed old and new attributes (both operations)
    """

    @pytest.fixture
    def hub(self, db):
        """Create an AttributeHub instance for testing."""
        from canvas_sdk.v1.data.custom_attribute import AttributeHub

        hub = AttributeHub(type="test", externally_exposable_id="test-123")
        hub.save()
        return hub

    # -------------------------------------------------------------------------
    # Scenario 1: All new attributes
    # -------------------------------------------------------------------------

    def test_all_new_attributes_creates_all(self, hub):
        """When no attributes exist, all should be created."""
        result = hub.set_attributes(
            {
                "name": "Test Name",
                "count": 42,
                "active": True,
            }
        )

        assert len(result) == 3

        # Verify attributes were created in database
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 3

        # Verify values are correct
        assert hub.get_attribute("name") == "Test Name"
        assert hub.get_attribute("count") == 42
        assert hub.get_attribute("active") is True

    def test_all_new_with_various_types(self, hub):
        """New attributes with various data types should all be created."""
        test_data = {
            "string_val": "hello",
            "int_val": 100,
            "bool_val": False,
            "float_val": 3.14,
            "json_val": {"nested": "data"},
            "list_val": [1, 2, 3],
        }

        result = hub.set_attributes(test_data)

        assert len(result) == 6

        # Verify each type is stored correctly
        assert hub.get_attribute("string_val") == "hello"
        assert hub.get_attribute("int_val") == 100
        assert hub.get_attribute("bool_val") is False
        # Floats are stored in DecimalField, so they come back as Decimal
        assert float(hub.get_attribute("float_val")) == 3.14
        assert hub.get_attribute("json_val") == {"nested": "data"}
        assert hub.get_attribute("list_val") == [1, 2, 3]

    def test_empty_dict_creates_nothing(self, hub):
        """Empty dict should create no attributes."""
        result = hub.set_attributes({})

        assert len(result) == 0
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 0

    # -------------------------------------------------------------------------
    # Scenario 2: All existing attributes to update
    # -------------------------------------------------------------------------

    def test_all_existing_attributes_updates_all(self, hub):
        """When all attributes exist, all should be updated."""
        # First create the attributes
        hub.set_attributes(
            {
                "name": "Original Name",
                "count": 10,
                "active": False,
            }
        )

        # Now update them all
        result = hub.set_attributes(
            {
                "name": "Updated Name",
                "count": 99,
                "active": True,
            }
        )

        assert len(result) == 3

        # Verify only 3 attributes exist (not 6)
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 3

        # Verify values are updated
        assert hub.get_attribute("name") == "Updated Name"
        assert hub.get_attribute("count") == 99
        assert hub.get_attribute("active") is True

    def test_update_changes_value_type(self, hub):
        """Updating can change the value type."""
        # Create with string
        hub.set_attributes({"flexible": "a string"})
        assert hub.get_attribute("flexible") == "a string"

        # Update to int
        hub.set_attributes({"flexible": 42})
        assert hub.get_attribute("flexible") == 42

        # Update to dict
        hub.set_attributes({"flexible": {"now": "json"}})
        assert hub.get_attribute("flexible") == {"now": "json"}

        # Should still be only one attribute
        assert CustomAttribute.objects.filter(object_id=hub.pk, name="flexible").count() == 1

    def test_update_to_same_value(self, hub):
        """Updating to the same value should work."""
        hub.set_attributes({"unchanged": "value"})

        result = hub.set_attributes({"unchanged": "value"})

        assert len(result) == 1
        assert hub.get_attribute("unchanged") == "value"

    # -------------------------------------------------------------------------
    # Scenario 3: Mixed old and new attributes
    # -------------------------------------------------------------------------

    def test_mixed_creates_and_updates(self, hub):
        """Mix of new and existing attributes should handle both."""
        # Create initial attributes
        hub.set_attributes(
            {
                "existing1": "original1",
                "existing2": 100,
            }
        )

        # Mixed update: update existing1, existing2 + create new1, new2
        result = hub.set_attributes(
            {
                "existing1": "updated1",
                "existing2": 200,
                "new1": "brand new",
                "new2": True,
            }
        )

        assert len(result) == 4

        # Verify total count
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 4

        # Verify existing were updated
        assert hub.get_attribute("existing1") == "updated1"
        assert hub.get_attribute("existing2") == 200

        # Verify new were created
        assert hub.get_attribute("new1") == "brand new"
        assert hub.get_attribute("new2") is True

    def test_mixed_with_partial_overlap(self, hub):
        """Some attributes exist, some are new."""
        # Create initial set
        hub.set_attributes(
            {
                "a": 1,
                "b": 2,
                "c": 3,
            }
        )

        # Update with partial overlap
        result = hub.set_attributes(
            {
                "b": 20,  # Update
                "d": 4,  # New
                "e": 5,  # New
            }
        )

        assert len(result) == 3

        # Total should be 5 attributes
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 5

        # Check all values
        assert hub.get_attribute("a") == 1  # Unchanged
        assert hub.get_attribute("b") == 20  # Updated
        assert hub.get_attribute("c") == 3  # Unchanged
        assert hub.get_attribute("d") == 4  # New
        assert hub.get_attribute("e") == 5  # New

    def test_mixed_single_update_multiple_creates(self, hub):
        """One existing attribute updated, multiple new created."""
        hub.set_attributes({"solo": "original"})

        result = hub.set_attributes(
            {
                "solo": "updated",
                "new1": "a",
                "new2": "b",
                "new3": "c",
            }
        )

        assert len(result) == 4
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 4

        assert hub.get_attribute("solo") == "updated"
        assert hub.get_attribute("new1") == "a"
        assert hub.get_attribute("new2") == "b"
        assert hub.get_attribute("new3") == "c"

    def test_mixed_multiple_updates_single_create(self, hub):
        """Multiple existing attributes updated, one new created."""
        hub.set_attributes(
            {
                "x": 1,
                "y": 2,
                "z": 3,
            }
        )

        result = hub.set_attributes(
            {
                "x": 10,
                "y": 20,
                "z": 30,
                "w": 4,  # New
            }
        )

        assert len(result) == 4
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 4

        assert hub.get_attribute("x") == 10
        assert hub.get_attribute("y") == 20
        assert hub.get_attribute("z") == 30
        assert hub.get_attribute("w") == 4

    # -------------------------------------------------------------------------
    # Edge cases and return value verification
    # -------------------------------------------------------------------------

    def test_returns_list_of_custom_attributes(self, hub):
        """Return value should be list of CustomAttribute instances."""
        result = hub.set_attributes(
            {
                "attr1": "value1",
                "attr2": "value2",
            }
        )

        assert isinstance(result, list)
        assert all(isinstance(attr, CustomAttribute) for attr in result)

    def test_returned_attributes_have_correct_values(self, hub):
        """Returned attributes should have the values that were set."""
        result = hub.set_attributes(
            {
                "name": "test",
                "count": 5,
            }
        )

        result_dict = {attr.name: attr.value for attr in result}

        assert result_dict["name"] == "test"
        assert result_dict["count"] == 5

    def test_multiple_calls_accumulate_attributes(self, hub):
        """Multiple set_attributes calls should accumulate (not replace all)."""
        hub.set_attributes({"batch1_a": 1, "batch1_b": 2})
        hub.set_attributes({"batch2_a": 3, "batch2_b": 4})
        hub.set_attributes({"batch3_a": 5})

        # All 5 attributes should exist
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 5

        assert hub.get_attribute("batch1_a") == 1
        assert hub.get_attribute("batch1_b") == 2
        assert hub.get_attribute("batch2_a") == 3
        assert hub.get_attribute("batch2_b") == 4
        assert hub.get_attribute("batch3_a") == 5
