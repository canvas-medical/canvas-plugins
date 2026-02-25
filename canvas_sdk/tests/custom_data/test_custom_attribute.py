"""Tests for CustomAttribute value setter and getter.

Tests verify that:
1. The setter correctly determines the data type and stores in the appropriate field
2. The getter returns the correct value from the appropriate field
3. Edge cases like bool vs int and datetime vs date are handled correctly
4. ModelExtensionMetaClass sets app_label correctly for proxy classes
"""

import datetime
import decimal
from typing import Any

import pytest

from canvas_sdk.v1.data.custom_attribute import (
    AttributeHub,
    CustomAttribute,
    ModelExtension,
    ModelExtensionMetaClass,
)


class TestCustomAttributeValueSetter:
    """Tests for the CustomAttribute.value setter."""

    @pytest.fixture
    def attr(self) -> CustomAttribute:
        """Create a fresh CustomAttribute instance for each test."""
        return CustomAttribute(name="test_attr")

    # -------------------------------------------------------------------------
    # String values
    # -------------------------------------------------------------------------

    def test_string_value_stored_in_text_value(self, attr: CustomAttribute) -> None:
        """String values should be stored in text_value field."""
        attr.value = "hello world"

        assert attr.text_value == "hello world"
        assert attr.int_value is None
        assert attr.bool_value is None
        assert attr.decimal_value is None
        assert attr.timestamp_value is None
        assert attr.date_value is None
        assert attr.json_value is None

    def test_empty_string_stored_in_text_value(self, attr: CustomAttribute) -> None:
        """Empty strings should be stored in text_value field."""
        attr.value = ""

        assert attr.text_value == ""

    def test_unicode_string_stored_in_text_value(self, attr: CustomAttribute) -> None:
        """Unicode strings should be stored in text_value field."""
        attr.value = "こんにちは世界 🌍"

        assert attr.text_value == "こんにちは世界 🌍"

    # -------------------------------------------------------------------------
    # Integer values
    # -------------------------------------------------------------------------

    def test_positive_int_stored_in_int_value(self, attr: CustomAttribute) -> None:
        """Positive integers should be stored in int_value field."""
        attr.value = 42

        assert attr.int_value == 42
        assert attr.text_value is None
        assert attr.bool_value is None
        assert attr.decimal_value is None
        assert attr.timestamp_value is None
        assert attr.date_value is None
        assert attr.json_value is None

    def test_negative_int_stored_in_int_value(self, attr: CustomAttribute) -> None:
        """Negative integers should be stored in int_value field."""
        attr.value = -100

        assert attr.int_value == -100

    def test_zero_stored_in_int_value(self, attr: CustomAttribute) -> None:
        """Zero should be stored in int_value field."""
        attr.value = 0

        assert attr.int_value == 0

    def test_large_int_stored_in_int_value(self, attr: CustomAttribute) -> None:
        """Large integers should be stored in int_value field."""
        attr.value = 2**31 - 1  # Max 32-bit signed int

        assert attr.int_value == 2**31 - 1

    # -------------------------------------------------------------------------
    # Boolean values - CRITICAL: bool is subclass of int in Python
    # -------------------------------------------------------------------------

    def test_true_stored_in_bool_value_not_int(self, attr: CustomAttribute) -> None:
        """True should go to bool_value, not int_value (even though bool is subclass of int)."""
        attr.value = True

        assert attr.bool_value is True
        assert attr.int_value is None  # NOT 1

    def test_false_stored_in_bool_value_not_int(self, attr: CustomAttribute) -> None:
        """False should go to bool_value, not int_value (even though bool is subclass of int)."""
        attr.value = False

        assert attr.bool_value is False
        assert attr.int_value is None  # NOT 0

    # -------------------------------------------------------------------------
    # Float values
    # -------------------------------------------------------------------------

    def test_float_stored_in_decimal_value(self, attr: CustomAttribute) -> None:
        """Float values should be stored in decimal_value field."""
        attr.value = 3.14159

        assert attr.decimal_value == 3.14159
        assert attr.int_value is None
        assert attr.text_value is None

    def test_negative_float_stored_in_decimal_value(self, attr: CustomAttribute) -> None:
        """Negative floats should be stored in decimal_value field."""
        attr.value = -273.15

        assert attr.decimal_value == -273.15

    def test_float_zero_stored_in_decimal_value(self, attr: CustomAttribute) -> None:
        """Float zero should be stored in decimal_value field."""
        attr.value = 0.0

        assert attr.decimal_value == 0.0

    # -------------------------------------------------------------------------
    # Decimal values
    # -------------------------------------------------------------------------

    def test_decimal_stored_in_decimal_value(self, attr: CustomAttribute) -> None:
        """Decimal values should be stored in decimal_value field."""
        attr.value = decimal.Decimal("123.456789")

        assert attr.decimal_value == decimal.Decimal("123.456789")

    def test_decimal_high_precision_stored_in_decimal_value(self, attr: CustomAttribute) -> None:
        """High-precision Decimal values should be stored in decimal_value field."""
        attr.value = decimal.Decimal("0.0000000001")

        assert attr.decimal_value == decimal.Decimal("0.0000000001")

    # -------------------------------------------------------------------------
    # Datetime values - CRITICAL: datetime is subclass of date in Python
    # -------------------------------------------------------------------------

    def test_datetime_stored_in_timestamp_value_not_date(self, attr: CustomAttribute) -> None:
        """Datetime should go to timestamp_value, not date_value."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45)
        attr.value = dt

        assert attr.timestamp_value == dt
        assert attr.date_value is None  # NOT the date part

    def test_datetime_with_timezone_stored_in_timestamp_value(self, attr: CustomAttribute) -> None:
        """Timezone-aware datetimes should be stored in timestamp_value field."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45, tzinfo=datetime.UTC)
        attr.value = dt

        assert attr.timestamp_value == dt

    def test_datetime_with_microseconds_stored_in_timestamp_value(
        self, attr: CustomAttribute
    ) -> None:
        """Datetimes with microseconds should be stored in timestamp_value field."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45, 123456)
        attr.value = dt

        assert attr.timestamp_value == dt

    # -------------------------------------------------------------------------
    # Date values
    # -------------------------------------------------------------------------

    def test_date_stored_in_date_value(self, attr: CustomAttribute) -> None:
        """Date values should be stored in date_value field."""
        d = datetime.date(2024, 1, 15)
        attr.value = d

        assert attr.date_value == d
        assert attr.timestamp_value is None

    # -------------------------------------------------------------------------
    # None value
    # -------------------------------------------------------------------------

    def test_none_clears_all_fields(self, attr: CustomAttribute) -> None:
        """Setting value to None should clear all typed fields."""
        # First set a value
        attr.value = "test"
        assert attr.text_value == "test"

        # Then set to None (the property setter mutates internal fields,
        # which mypy cannot track — hence the type: ignore below)
        attr.value = None

        assert attr.text_value is None
        assert attr.int_value is None  # type: ignore[unreachable]
        assert attr.bool_value is None
        assert attr.decimal_value is None
        assert attr.timestamp_value is None
        assert attr.date_value is None
        assert attr.json_value is None

    # -------------------------------------------------------------------------
    # JSON/complex values
    # -------------------------------------------------------------------------

    def test_dict_stored_in_json_value(self, attr: CustomAttribute) -> None:
        """Dict values should be stored in json_value field."""
        data = {"key": "value", "nested": {"a": 1}}
        attr.value = data

        assert attr.json_value == data
        assert attr.text_value is None

    def test_list_stored_in_json_value(self, attr: CustomAttribute) -> None:
        """List values should be stored in json_value field."""
        data = [1, 2, 3, "four", {"five": 5}]
        attr.value = data

        assert attr.json_value == data

    def test_empty_dict_stored_in_json_value(self, attr: CustomAttribute) -> None:
        """Empty dicts should be stored in json_value field."""
        attr.value = {}

        assert attr.json_value == {}

    def test_empty_list_stored_in_json_value(self, attr: CustomAttribute) -> None:
        """Empty lists should be stored in json_value field."""
        attr.value = []

        assert attr.json_value == []

    # -------------------------------------------------------------------------
    # Value replacement clears previous field
    # -------------------------------------------------------------------------

    def test_changing_type_clears_previous_field(self, attr: CustomAttribute) -> None:
        """Setting a new value type should clear the old field."""
        attr.value = "string"
        assert attr.text_value == "string"

        # Property setter mutates fields mypy can't track
        attr.value = 42
        assert attr.int_value == 42
        assert attr.text_value is None

    def test_multiple_type_changes(self, attr: CustomAttribute) -> None:
        """Test cycling through multiple types."""
        attr.value = "text"
        assert attr.text_value == "text"

        # Property setter mutates fields mypy can't track
        attr.value = 123
        assert attr.int_value == 123
        assert attr.text_value is None

        attr.value = True  # type: ignore[unreachable]
        assert attr.bool_value is True
        assert attr.int_value is None
        attr.value = {"json": True}
        assert attr.json_value == {"json": True}
        assert attr.bool_value is None


class TestCustomAttributeValueGetter:
    """Tests for the CustomAttribute.value getter."""

    @pytest.fixture
    def attr(self) -> CustomAttribute:
        """Create a fresh CustomAttribute instance for each test."""
        return CustomAttribute(name="test_attr")

    # -------------------------------------------------------------------------
    # Get values from each field type
    # -------------------------------------------------------------------------

    def test_get_text_value(self, attr: CustomAttribute) -> None:
        """Getter should return text_value when it is set."""
        attr.text_value = "hello"

        assert attr.value == "hello"

    def test_get_int_value(self, attr: CustomAttribute) -> None:
        """Getter should return int_value when it is set."""
        attr.int_value = 42

        assert attr.value == 42

    def test_get_bool_value_true(self, attr: CustomAttribute) -> None:
        """Getter should return True from bool_value."""
        attr.bool_value = True

        assert attr.value is True

    def test_get_bool_value_false(self, attr: CustomAttribute) -> None:
        """Getter should return False from bool_value."""
        attr.bool_value = False

        assert attr.value is False

    def test_get_decimal_value(self, attr: CustomAttribute) -> None:
        """Getter should return decimal_value when it is set."""
        attr.decimal_value = decimal.Decimal("3.14")

        assert attr.value == decimal.Decimal("3.14")

    def test_get_timestamp_value(self, attr: CustomAttribute) -> None:
        """Getter should return timestamp_value when it is set."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45)
        attr.timestamp_value = dt

        assert attr.value == dt

    def test_get_date_value(self, attr: CustomAttribute) -> None:
        """Getter should return date_value when it is set."""
        d = datetime.date(2024, 1, 15)
        attr.date_value = d

        assert attr.value == d

    def test_get_json_value_dict(self, attr: CustomAttribute) -> None:
        """Getter should return dict from json_value."""
        attr.json_value = {"key": "value"}

        assert attr.value == {"key": "value"}

    def test_get_json_value_list(self, attr: CustomAttribute) -> None:
        """Getter should return list from json_value."""
        attr.json_value = [1, 2, 3]

        assert attr.value == [1, 2, 3]

    # -------------------------------------------------------------------------
    # Get None when no value is set
    # -------------------------------------------------------------------------

    def test_get_returns_none_when_all_fields_empty(self, attr: CustomAttribute) -> None:
        """Getter should return None when no typed field is set."""
        assert attr.value is None

    # -------------------------------------------------------------------------
    # Round-trip tests (set then get)
    # -------------------------------------------------------------------------

    def test_roundtrip_string(self, attr: CustomAttribute) -> None:
        """String value should survive a set/get round-trip."""
        attr.value = "test string"
        assert attr.value == "test string"

    def test_roundtrip_int(self, attr: CustomAttribute) -> None:
        """Integer value should survive a set/get round-trip."""
        attr.value = 12345
        assert attr.value == 12345

    def test_roundtrip_bool_true(self, attr: CustomAttribute) -> None:
        """True should survive a set/get round-trip."""
        attr.value = True
        assert attr.value is True

    def test_roundtrip_bool_false(self, attr: CustomAttribute) -> None:
        """False should survive a set/get round-trip."""
        attr.value = False
        assert attr.value is False

    def test_roundtrip_float(self, attr: CustomAttribute) -> None:
        """Float value should survive a set/get round-trip."""
        attr.value = 3.14159
        assert attr.value == 3.14159

    def test_roundtrip_decimal(self, attr: CustomAttribute) -> None:
        """Decimal value should survive a set/get round-trip."""
        attr.value = decimal.Decimal("999.99")
        assert attr.value == decimal.Decimal("999.99")

    def test_roundtrip_datetime(self, attr: CustomAttribute) -> None:
        """Datetime value should survive a set/get round-trip."""
        dt = datetime.datetime(2024, 6, 15, 14, 30, 0)
        attr.value = dt
        assert attr.value == dt

    def test_roundtrip_date(self, attr: CustomAttribute) -> None:
        """Date value should survive a set/get round-trip."""
        d = datetime.date(2024, 6, 15)
        attr.value = d
        assert attr.value == d

    def test_roundtrip_dict(self, attr: CustomAttribute) -> None:
        """Dict value should survive a set/get round-trip."""
        data = {"nested": {"data": [1, 2, 3]}}
        attr.value = data
        assert attr.value == data

    def test_roundtrip_list(self, attr: CustomAttribute) -> None:
        """List value should survive a set/get round-trip."""
        data = ["a", "b", "c"]
        attr.value = data
        assert attr.value == data

    def test_roundtrip_none(self, attr: CustomAttribute) -> None:
        """Setting None after a value should clear it."""
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
    def attr(self) -> CustomAttribute:
        """Create a fresh CustomAttribute instance for each test."""
        return CustomAttribute(name="test_attr")

    def test_bool_true_is_not_stored_as_int_1(self, attr: CustomAttribute) -> None:
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

    def test_bool_false_is_not_stored_as_int_0(self, attr: CustomAttribute) -> None:
        """Verify False goes to bool_value, not int_value as 0."""
        attr.value = False

        assert attr.bool_value is False
        assert attr.int_value is None

        retrieved = attr.value
        assert retrieved is False
        assert type(retrieved) is bool

    def test_int_1_is_not_stored_as_bool_true(self, attr: CustomAttribute) -> None:
        """Verify 1 goes to int_value, not bool_value as True."""
        attr.value = 1

        assert attr.int_value == 1
        assert attr.bool_value is None

        retrieved = attr.value
        assert retrieved == 1
        assert type(retrieved) is int

    def test_int_0_is_not_stored_as_bool_false(self, attr: CustomAttribute) -> None:
        """Verify 0 goes to int_value, not bool_value as False."""
        attr.value = 0

        assert attr.int_value == 0
        assert attr.bool_value is None

        retrieved = attr.value
        assert retrieved == 0
        assert type(retrieved) is int

    def test_datetime_is_not_stored_as_date(self, attr: CustomAttribute) -> None:
        """Verify datetime goes to timestamp_value, not date_value."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 45)
        attr.value = dt

        assert attr.timestamp_value == dt
        assert attr.date_value is None

        retrieved = attr.value
        assert retrieved == dt
        assert type(retrieved) is datetime.datetime

    def test_date_is_stored_as_date_not_datetime(self, attr: CustomAttribute) -> None:
        """Verify date goes to date_value, not timestamp_value."""
        d = datetime.date(2024, 1, 15)
        attr.value = d

        assert attr.date_value == d
        assert attr.timestamp_value is None

        # Note: The getter will return the date value
        retrieved = attr.value
        assert retrieved == d

    def test_float_is_not_confused_with_int(self, attr: CustomAttribute) -> None:
        """Verify float goes to decimal_value, not int_value."""
        attr.value = 1.0  # This is a float, even though it equals int 1

        assert attr.decimal_value == 1.0
        assert attr.int_value is None

    def test_decimal_is_not_confused_with_float(self, attr: CustomAttribute) -> None:
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
    def attr(self) -> CustomAttribute:
        """Create a fresh CustomAttribute instance for each test."""
        return CustomAttribute(name="test_attr")

    def test_text_value_has_priority(self, attr: CustomAttribute) -> None:
        """text_value is checked first in the getter."""
        attr.text_value = "text"
        attr.int_value = 42

        assert attr.value == "text"

    def test_date_value_before_timestamp_value(self, attr: CustomAttribute) -> None:
        """date_value is checked before timestamp_value."""
        attr.date_value = datetime.date(2024, 1, 1)
        attr.timestamp_value = datetime.datetime(2024, 6, 15, 10, 0, 0)

        assert attr.value == datetime.date(2024, 1, 1)

    def test_int_value_before_decimal_value(self, attr: CustomAttribute) -> None:
        """int_value is checked before decimal_value."""
        attr.int_value = 42
        attr.decimal_value = decimal.Decimal("3.14")

        assert attr.value == 42


# ===========================================================================
# Tests for ModelExtensionMetaClass app_label behavior
# ===========================================================================


class TestModelExtensionMetaClassAppLabel:
    """Tests that ModelExtensionMetaClass sets app_label correctly.

    The metaclass sets app_label based on __module__:
    - If __module__ starts with "canvas_sdk", app_label is NOT set by metaclass
    - If __module__ does NOT start with "canvas_sdk" (e.g., a plugin),
      app_label is set to the first part of the module name
    """

    def test_plugin_module_gets_app_label_from_module_name(self) -> None:
        """Classes in plugin modules should get app_label from first module part."""
        # Simulate a class defined in "my_plugin.models.custom"
        attrs = {
            "__module__": "my_plugin.models.custom",
            "__qualname__": "MyPluginModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        # The metaclass should set app_label to "my_plugin"
        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "MyPluginModel",
            (ModelExtension,),
            attrs,
        )

        assert meta.app_label == "my_plugin"

    def test_deeply_nested_plugin_module_gets_first_part(self) -> None:
        """Deeply nested modules should still get first part as app_label."""
        attrs = {
            "__module__": "awesome_plugin.sub.models.deeply.nested",
            "__qualname__": "DeepModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "DeepModel",
            (ModelExtension,),
            attrs,
        )

        assert meta.app_label == "awesome_plugin"

    def test_canvas_sdk_module_does_not_override_app_label(self) -> None:
        """Classes in canvas_sdk modules should NOT have app_label set by metaclass."""
        attrs = {
            "__module__": "canvas_sdk.v1.data.custom_attribute",
            "__qualname__": "SdkModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        # Ensure app_label is not set initially
        assert not hasattr(meta, "app_label")

        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "SdkModel",
            (ModelExtension,),
            attrs,
        )

        # app_label should NOT be set by the metaclass for canvas_sdk modules
        assert not hasattr(meta, "app_label")

    def test_canvas_sdk_submodule_does_not_override_app_label(self) -> None:
        """Any canvas_sdk.* module should not have app_label overridden."""
        attrs = {
            "__module__": "canvas_sdk.effects.something",
            "__qualname__": "EffectModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "EffectModel",
            (ModelExtension,),
            attrs,
        )

        assert not hasattr(meta, "app_label")

    def test_single_word_module_name(self) -> None:
        """Single word module names should work (edge case)."""
        attrs = {
            "__module__": "myplugin",
            "__qualname__": "SimpleModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "SimpleModel",
            (ModelExtension,),
            attrs,
        )

        assert meta.app_label == "myplugin"

    def test_meta_class_created_if_not_provided(self) -> None:
        """If Meta is not provided, it should be created and app_label set."""
        attrs = {
            "__module__": "test_plugin.models",
            "__qualname__": "NoMetaModel",
            # No Meta class provided
        }

        new_class: Any = ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "NoMetaModel",
            (ModelExtension,),
            attrs,
        )

        # The created class should have app_label set correctly
        assert new_class._meta.app_label == "test_plugin"

    def test_existing_app_label_overwritten_for_plugins(self) -> None:
        """Existing app_label should be overwritten for plugin modules."""
        attrs = {
            "__module__": "new_plugin.models",
            "__qualname__": "OverwriteModel",
            "Meta": type("Meta", (), {"abstract": True, "app_label": "old_label"}),
        }

        meta: Any = attrs["Meta"]
        assert meta.app_label == "old_label"

        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "OverwriteModel",
            (ModelExtension,),
            attrs,
        )

        # Should be overwritten to match module
        assert meta.app_label == "new_plugin"

    def test_hyphenated_plugin_name(self) -> None:
        """Plugin names with hyphens should work."""
        attrs = {
            "__module__": "my-cool-plugin.models",
            "__qualname__": "HyphenModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "HyphenModel",
            (ModelExtension,),
            attrs,
        )

        assert meta.app_label == "my-cool-plugin"

    def test_underscored_plugin_name(self) -> None:
        """Plugin names with underscores should work."""
        attrs = {
            "__module__": "my_cool_plugin.models.data",
            "__qualname__": "UnderscoreModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "UnderscoreModel",
            (ModelExtension,),
            attrs,
        )

        assert meta.app_label == "my_cool_plugin"


# ===========================================================================
# Tests for ModelExtensionMetaClass auto-proxy behavior
# ===========================================================================


class TestModelExtensionMetaClassAutoProxy:
    """Tests that ModelExtensionMetaClass auto-sets proxy = True.

    The metaclass should auto-set proxy = True when:
    - The class is defined in a non-SDK module
    - The class has a concrete (non-abstract) base model
    - The Meta class does not already set proxy or abstract
    """

    def test_plugin_subclass_of_concrete_model_gets_proxy_true(self) -> None:
        """A plugin class extending a concrete model should auto-get proxy = True."""
        attrs: dict[str, Any] = {
            "__module__": "my_plugin.models",
            "__qualname__": "MyProxy",
        }

        new_class: Any = ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "MyProxy",
            (AttributeHub, ModelExtension),
            attrs,
        )

        assert new_class._meta.proxy is True

    def test_plugin_subclass_explicit_proxy_false_is_respected(self) -> None:
        """If a plugin explicitly sets proxy = False, the metaclass should not override it."""
        attrs: dict[str, Any] = {
            "__module__": "my_plugin.models",
            "__qualname__": "MyModel",
            "Meta": type("Meta", (), {"proxy": False}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "MyModel",
            (AttributeHub, ModelExtension),
            attrs,
        )

        assert meta.proxy is False

    def test_plugin_abstract_class_does_not_get_proxy(self) -> None:
        """Abstract plugin classes should not get proxy = True."""
        attrs: dict[str, Any] = {
            "__module__": "my_plugin.models",
            "__qualname__": "MyAbstract",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "MyAbstract",
            (ModelExtension,),
            attrs,
        )

        assert not getattr(meta, "proxy", False)

    def test_sdk_class_does_not_get_auto_proxy(self) -> None:
        """Classes defined in canvas_sdk should not get proxy auto-set."""
        attrs: dict[str, Any] = {
            "__module__": "canvas_sdk.v1.data.something",
            "__qualname__": "SdkModel",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "SdkModel",
            (AttributeHub, ModelExtension),
            attrs,
        )

        assert not getattr(meta, "proxy", False)

    def test_mixin_only_base_does_not_get_proxy(self) -> None:
        """A class that only extends ModelExtension (no concrete model) should not get proxy."""
        attrs: dict[str, Any] = {
            "__module__": "my_plugin.models",
            "__qualname__": "MixinOnly",
            "Meta": type("Meta", (), {"abstract": True}),
        }

        meta: Any = attrs["Meta"]
        ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "MixinOnly",
            (ModelExtension,),
            attrs,
        )

        assert not getattr(meta, "proxy", False)


# ===========================================================================
# Tests for ModelExtension auto-manager assignment
# ===========================================================================


class TestModelExtensionAutoManager:
    """Tests that ModelExtension auto-assigns CustomAttributeAwareManager."""

    def test_subclass_gets_aware_manager_automatically(self) -> None:
        """A subclass without an explicit manager should get CustomAttributeAwareManager."""
        new_class: Any = ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "AutoManagerModel",
            (AttributeHub, ModelExtension),
            {
                "__module__": "my_plugin.models",
                "__qualname__": "AutoManagerModel",
            },
        )

        from canvas_sdk.v1.data.custom_attribute import CustomAttributeAwareManager

        assert isinstance(new_class.objects, CustomAttributeAwareManager)

    def test_explicit_manager_is_not_overwritten(self) -> None:
        """A subclass with an explicit objects manager should keep it."""
        from django.db import models as dj_models

        custom_manager: dj_models.Manager[Any] = dj_models.Manager()
        new_class: Any = ModelExtensionMetaClass.__new__(
            ModelExtensionMetaClass,
            "ExplicitManagerModel",
            (AttributeHub, ModelExtension),
            {
                "__module__": "my_plugin.models",
                "__qualname__": "ExplicitManagerModel",
                "objects": custom_manager,
            },
        )

        assert new_class.objects is not None
        from canvas_sdk.v1.data.custom_attribute import CustomAttributeAwareManager

        assert not isinstance(new_class.objects, CustomAttributeAwareManager)


# ===========================================================================
# Tests for set_attribute (single attribute)
# ===========================================================================


@pytest.mark.django_db
class TestSetAttribute:
    """Tests for ModelExtension.set_attribute method."""

    @pytest.fixture
    def hub(self, db: None) -> AttributeHub:
        """Create an AttributeHub instance for testing."""
        hub = AttributeHub(type="test", id="set-attr-test")
        hub.save()
        return hub

    def test_creates_new_attribute(self, hub: AttributeHub) -> None:
        """Should create a new CustomAttribute and return it."""
        result = hub.set_attribute("color", "blue")

        assert isinstance(result, CustomAttribute)
        assert result.name == "color"
        assert result.value == "blue"
        assert CustomAttribute.objects.filter(object_id=hub.pk, name="color").count() == 1

    def test_updates_existing_attribute(self, hub: AttributeHub) -> None:
        """Should update the value of an existing attribute in-place."""
        hub.set_attribute("color", "blue")
        hub.set_attribute("color", "red")

        assert hub.get_attribute("color") == "red"
        # Should still be only one row, not two
        assert CustomAttribute.objects.filter(object_id=hub.pk, name="color").count() == 1

    def test_returns_custom_attribute_instance(self, hub: AttributeHub) -> None:
        """Return value should be a persisted CustomAttribute."""
        result = hub.set_attribute("key", "value")

        assert result.pk is not None
        assert result.name == "key"

    def test_stores_various_types(self, hub: AttributeHub) -> None:
        """Should correctly store and retrieve different value types."""
        hub.set_attribute("text", "hello")
        hub.set_attribute("integer", 42)
        hub.set_attribute("boolean", True)
        hub.set_attribute("json_data", {"nested": [1, 2]})

        assert hub.get_attribute("text") == "hello"
        assert hub.get_attribute("integer") == 42
        assert hub.get_attribute("boolean") is True
        assert hub.get_attribute("json_data") == {"nested": [1, 2]}

    def test_multiple_attributes_on_same_instance(self, hub: AttributeHub) -> None:
        """Setting different attribute names should create separate records."""
        hub.set_attribute("a", 1)
        hub.set_attribute("b", 2)
        hub.set_attribute("c", 3)

        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 3
        assert hub.get_attribute("a") == 1
        assert hub.get_attribute("b") == 2
        assert hub.get_attribute("c") == 3


# ===========================================================================
# Tests for set_attributes bulk operation logic
# ===========================================================================


@pytest.mark.django_db
class TestSetAttributesBulkOperations:
    """Tests for ModelExtension.set_attributes method.

    Tests cover the three main scenarios:
    1. All new attributes (bulk_create only)
    2. All existing attributes to update (bulk_update only)
    3. Mixed old and new attributes (both operations)
    """

    @pytest.fixture
    def hub(self, db: None) -> AttributeHub:
        """Create an AttributeHub instance for testing."""
        hub = AttributeHub(type="test", id="test-123")
        hub.save()
        return hub

    # -------------------------------------------------------------------------
    # Scenario 1: All new attributes
    # -------------------------------------------------------------------------

    def test_all_new_attributes_creates_all(self, hub: AttributeHub) -> None:
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

    def test_all_new_with_various_types(self, hub: AttributeHub) -> None:
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

    def test_empty_dict_creates_nothing(self, hub: AttributeHub) -> None:
        """Empty dict should create no attributes."""
        result = hub.set_attributes({})

        assert len(result) == 0
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 0

    # -------------------------------------------------------------------------
    # Scenario 2: All existing attributes to update
    # -------------------------------------------------------------------------

    def test_all_existing_attributes_updates_all(self, hub: AttributeHub) -> None:
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

    def test_update_changes_value_type(self, hub: AttributeHub) -> None:
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

    def test_update_date_value(self, hub: AttributeHub) -> None:
        """Updating a date attribute via bulk update should persist the new value."""
        original_date = datetime.date(2024, 1, 1)
        hub.set_attributes({"birthday": original_date})
        assert hub.get_attribute("birthday") == original_date

        # Update the date — this exercises the bulk_update path with date_value
        updated_date = datetime.date(2025, 6, 15)
        hub.set_attributes({"birthday": updated_date})

        # Re-fetch from database to confirm persistence
        attr = CustomAttribute.objects.get(object_id=hub.pk, name="birthday")
        assert attr.date_value == updated_date
        assert attr.value == updated_date

    def test_update_all_value_types(self, hub: AttributeHub) -> None:
        """Updating all value types via bulk update should persist every field."""
        initial = {
            "text_attr": "original",
            "date_attr": datetime.date(2024, 1, 1),
            "datetime_attr": datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC),
            "int_attr": 1,
            "decimal_attr": decimal.Decimal("1.5"),
            "bool_attr": False,
            "json_attr": {"key": "old"},
        }
        hub.set_attributes(initial)

        updated = {
            "text_attr": "updated",
            "date_attr": datetime.date(2025, 6, 15),
            "datetime_attr": datetime.datetime(2025, 6, 15, 18, 30, 0, tzinfo=datetime.UTC),
            "int_attr": 99,
            "decimal_attr": decimal.Decimal("99.99"),
            "bool_attr": True,
            "json_attr": {"key": "new"},
        }
        hub.set_attributes(updated)

        # Verify total count unchanged (all updates, no creates)
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 7

        # Re-fetch from database to confirm persistence
        for name, expected in updated.items():
            attr = CustomAttribute.objects.get(object_id=hub.pk, name=name)
            assert attr.value == expected, f"{name}: expected {expected!r}, got {attr.value!r}"

    def test_update_to_same_value(self, hub: AttributeHub) -> None:
        """Updating to the same value should work."""
        hub.set_attributes({"unchanged": "value"})

        result = hub.set_attributes({"unchanged": "value"})

        assert len(result) == 1
        assert hub.get_attribute("unchanged") == "value"

    # -------------------------------------------------------------------------
    # Scenario 3: Mixed old and new attributes
    # -------------------------------------------------------------------------

    def test_mixed_creates_and_updates(self, hub: AttributeHub) -> None:
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

    def test_mixed_with_partial_overlap(self, hub: AttributeHub) -> None:
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

    def test_mixed_single_update_multiple_creates(self, hub: AttributeHub) -> None:
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

    def test_mixed_multiple_updates_single_create(self, hub: AttributeHub) -> None:
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

    def test_returns_list_of_custom_attributes(self, hub: AttributeHub) -> None:
        """Return value should be list of CustomAttribute instances."""
        result = hub.set_attributes(
            {
                "attr1": "value1",
                "attr2": "value2",
            }
        )

        assert isinstance(result, list)
        assert all(isinstance(attr, CustomAttribute) for attr in result)

    def test_returned_attributes_have_correct_values(self, hub: AttributeHub) -> None:
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

    def test_multiple_calls_accumulate_attributes(self, hub: AttributeHub) -> None:
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


# ===========================================================================
# Tests for delete_attribute
# ===========================================================================


@pytest.mark.django_db
class TestDeleteAttribute:
    """Tests for ModelExtension.delete_attribute method."""

    @pytest.fixture
    def hub(self, db: None) -> AttributeHub:
        """Create an AttributeHub instance for testing."""
        hub = AttributeHub(type="test", id="delete-test")
        hub.save()
        return hub

    def test_deletes_existing_attribute(self, hub: AttributeHub) -> None:
        """Should delete the attribute and return True."""
        hub.set_attribute("to_delete", "value")
        assert hub.get_attribute("to_delete") == "value"

        result = hub.delete_attribute("to_delete")

        assert result is True
        assert hub.get_attribute("to_delete") is None
        assert CustomAttribute.objects.filter(object_id=hub.pk, name="to_delete").count() == 0

    def test_returns_false_for_nonexistent_attribute(self, hub: AttributeHub) -> None:
        """Should return False when the attribute doesn't exist."""
        result = hub.delete_attribute("nonexistent")

        assert result is False

    def test_does_not_affect_other_attributes(self, hub: AttributeHub) -> None:
        """Deleting one attribute should leave others intact."""
        hub.set_attribute("keep", "kept")
        hub.set_attribute("remove", "removed")

        hub.delete_attribute("remove")

        assert hub.get_attribute("keep") == "kept"
        assert CustomAttribute.objects.filter(object_id=hub.pk).count() == 1
