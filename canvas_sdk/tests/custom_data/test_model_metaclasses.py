"""Tests for proxy_field descriptor, metaclass behavior, and proxy model scoping.

Tests verify that:
1. Accessing a proxy_field returns an instance of the proxy class
2. Null FKs return None without error
3. Assignment delegates to the parent descriptor
4. Accessing on the class returns the descriptor itself
5. __set_name__ correctly finds the parent descriptor from MRO
6. CustomModelMetaclass rejects non-namespaced related_name on SDK model targets
7. CustomModelMetaclass allows bare related_name on proxy/CustomModel targets
8. Proxy model reverse relations are scoped correctly
9. ModelExtensionMetaClass sets app_label from __module__ for plugin classes
10. ModelExtensionMetaClass auto-sets proxy = True for plugin subclasses of concrete models
"""

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from django.db import models
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from canvas_sdk.v1.data.base import (
    CustomModel,
    Model,
    ModelExtension,
    ModelExtensionMetaClass,
    proxy_field,
)
from canvas_sdk.v1.data.custom_attribute import AttributeHub

# ---------------------------------------------------------------------------
# Stub models for proxy_field descriptor tests
# ---------------------------------------------------------------------------


class FakeProxyClass:
    """Stub proxy class for testing __class__ swapping."""

    pass


class FakeParentModel:
    """Simulates a base model class with a FK descriptor."""

    pass


# ---------------------------------------------------------------------------
# Stub models for related_name validation / proxy scoping tests
# ---------------------------------------------------------------------------


class SDKModel(Model):
    """A stand-in for an SDK model (inherits from Model, not CustomModel).

    FK/OneToOne fields targeting this must use a namespaced related_name
    because SDK models are shared across plugins.
    """

    class Meta:
        app_label = "canvas_sdk"
        managed = False


class NamespacedRelatedNameModel(CustomModel):
    """A model with a template-namespaced related_name targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.ForeignKey(
        SDKModel, on_delete=models.DO_NOTHING, related_name="%(app_label)s_custom"
    )


class HardcodedNamespacedModel(CustomModel):
    """A model with a hardcoded app_label prefix in related_name targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.ForeignKey(
        SDKModel, on_delete=models.DO_NOTHING, related_name="canvas_sdk_hardcoded"
    )


class PlusRelatedNameModel(CustomModel):
    """A model with related_name='+' (no reverse relation) targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.ForeignKey(SDKModel, on_delete=models.DO_NOTHING, related_name="+")


class NoExplicitRelatedNameModel(CustomModel):
    """A model with no explicit related_name targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.OneToOneField(SDKModel, on_delete=models.DO_NOTHING)


class SDKModelProxy(SDKModel, ModelExtension):
    """A proxy of an SDK model, as plugins typically create."""

    class Meta:
        app_label = "test_plugin"
        proxy = True


class ProxyTargetModel(CustomModel):
    """A model with a non-namespaced related_name on a FK targeting a proxy model.

    This is allowed because proxy models are plugin-private — each plugin's
    proxy has its own app_label, so reverse relations are scoped to the proxy.
    """

    class Meta:
        app_label = "test_plugin"

    proxy_ref = models.OneToOneField(
        SDKModelProxy, on_delete=models.DO_NOTHING, related_name="biography"
    )


class SDKModelProxyB(SDKModel, ModelExtension):
    """A second proxy of SDKModel, used to verify related_name isolation."""

    class Meta:
        app_label = "test_plugin"
        proxy = True


class AttachedToProxyA(CustomModel):
    """A CustomModel with a FK to SDKModelProxy (proxy A), not SDKModelProxyB."""

    class Meta:
        app_label = "test_plugin"

    proxy_a_ref = models.ForeignKey(
        SDKModelProxy, on_delete=models.DO_NOTHING, related_name="attached_records"
    )


# ===========================================================================
# Tests for proxy_field descriptor
# ===========================================================================


@pytest.fixture
def parent_descriptor() -> MagicMock:
    """Create a mock ForwardManyToOneDescriptor with descriptor protocol support."""
    desc = MagicMock(spec=ForwardManyToOneDescriptor)
    desc.__set__ = MagicMock()
    return desc


@pytest.fixture
def descriptor_with_parent(parent_descriptor: MagicMock) -> proxy_field:
    """Create a proxy_field and wire up its parent descriptor."""
    pf = proxy_field(FakeProxyClass)
    pf._parent_descriptor = parent_descriptor
    return pf


def test_get_returns_proxy_class(
    descriptor_with_parent: proxy_field, parent_descriptor: MagicMock
) -> None:
    """Accessing the field on an instance returns an object whose class is the proxy class."""
    related_obj = MagicMock()
    parent_descriptor.__get__ = MagicMock(return_value=related_obj)

    obj = MagicMock()
    result = descriptor_with_parent.__get__(obj, type(obj))

    parent_descriptor.__get__.assert_called_once_with(obj, type(obj))
    assert result.__class__ is FakeProxyClass


def test_get_returns_none_when_null(
    descriptor_with_parent: proxy_field, parent_descriptor: MagicMock
) -> None:
    """Null FKs return None without attempting to swap __class__."""
    parent_descriptor.__get__ = MagicMock(return_value=None)

    obj = MagicMock()
    result = descriptor_with_parent.__get__(obj, type(obj))

    assert result is None


def test_set_delegates_to_parent(
    descriptor_with_parent: proxy_field, parent_descriptor: MagicMock
) -> None:
    """Assignment delegates to the parent descriptor's __set__."""
    obj = MagicMock()
    value = MagicMock()

    descriptor_with_parent.__set__(obj, value)

    parent_descriptor.__set__.assert_called_once_with(obj, value)


def test_class_access_returns_descriptor(descriptor_with_parent: proxy_field) -> None:
    """Accessing on the class (obj is None) returns the descriptor itself."""
    result = descriptor_with_parent.__get__(None, FakeParentModel)
    assert result is descriptor_with_parent


def test_set_name_finds_parent_descriptor() -> None:
    """__set_name__ correctly walks MRO and finds the parent descriptor."""
    parent_desc = MagicMock(spec=ForwardManyToOneDescriptor)

    # Build a class hierarchy where the base has a descriptor named "patient"
    BaseModel = type("BaseModel", (), {"patient": parent_desc})
    ChildModel = type("ChildModel", (BaseModel,), {})

    pf = proxy_field(FakeProxyClass)
    pf.__set_name__(ChildModel, "patient")

    assert pf._parent_descriptor is parent_desc


# ===========================================================================
# Tests for CustomModelMetaclass related_name auto-namespacing
# ===========================================================================


class TestCustomModelMetaclassRelatedName:
    """Tests that CustomModelMetaclass rejects non-namespaced related_name on
    FK/OneToOne fields targeting SDK models, while allowing them on fields
    targeting other CustomModels or proxy models.
    """

    def test_non_namespaced_related_name_to_sdk_model_raises(self) -> None:
        """A bare related_name on a FK to an SDK model should raise ValueError."""
        with pytest.raises(ValueError, match="related_name='status'.*SDK model.*SDKModel"):
            type(
                "BadModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "BadModel",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "sdk_ref": models.ForeignKey(
                        SDKModel, on_delete=models.DO_NOTHING, related_name="status"
                    ),
                },
            )

    def test_template_namespaced_related_name_to_sdk_model_is_allowed(self) -> None:
        """A %(app_label)s-prefixed related_name on a FK to an SDK model should be accepted."""
        field = NamespacedRelatedNameModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.related_name == "canvas_sdk_custom"

    def test_hardcoded_namespaced_related_name_to_sdk_model_is_allowed(self) -> None:
        """A related_name with hardcoded app_label_ prefix should be accepted."""
        field = HardcodedNamespacedModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.related_name == "canvas_sdk_hardcoded"

    def test_plus_related_name_to_sdk_model_is_allowed(self) -> None:
        """related_name='+' should be accepted for SDK model targets."""
        field = PlusRelatedNameModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.related_name == "+"

    def test_no_explicit_related_name_to_sdk_model_is_allowed(self) -> None:
        """No explicit related_name on a FK to an SDK model should be accepted."""
        # Django assigns None as the related_name when not specified.
        field = NoExplicitRelatedNameModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.OneToOneField)
        assert field.remote_field.related_name is None

    def test_non_namespaced_related_name_to_proxy_model_is_allowed(self) -> None:
        """A bare related_name on a FK to a proxy model should be accepted."""
        field = ProxyTargetModel._meta.get_field("proxy_ref")
        assert isinstance(field, models.OneToOneField)
        assert field.remote_field.related_name == "biography"

    def test_string_ref_to_same_app_model_allows_bare_related_name(self) -> None:
        """A bare related_name on a string-based FK to a model in the same app should be allowed.

        String FK references (e.g. "OrderItem") are not resolved at metaclass time,
        so the check infers that unqualified strings target the same app — which is
        always plugin-private for CustomModels.
        """
        # Circular reference: Order → "StringTargetModel" (forward ref within same app).
        # Should NOT raise even though related_name is not namespaced.
        type(
            "StringRefModel",
            (CustomModel,),
            {
                "__module__": "some_plugin.models",
                "__qualname__": "StringRefModel",
                "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                "other": models.ForeignKey(
                    "StringTargetModel",
                    on_delete=models.DO_NOTHING,
                    related_name="back_refs",
                ),
            },
        )

    def test_string_self_ref_allows_bare_related_name(self) -> None:
        """A bare related_name on a self-referential FK using "self" should be allowed."""
        type(
            "SelfRefModel",
            (CustomModel,),
            {
                "__module__": "some_plugin.models",
                "__qualname__": "SelfRefModel",
                "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                "parent": models.ForeignKey(
                    "self",
                    on_delete=models.DO_NOTHING,
                    null=True,
                    related_name="children",
                ),
            },
        )

    def test_qualified_string_ref_to_same_app_allows_bare_related_name(self) -> None:
        """A bare related_name on a qualified string FK within the same app should be allowed."""
        type(
            "QualifiedStringRefModel",
            (CustomModel,),
            {
                "__module__": "some_plugin.models",
                "__qualname__": "QualifiedStringRefModel",
                "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                "other": models.ForeignKey(
                    "some_plugin.SomeOtherModel",
                    on_delete=models.DO_NOTHING,
                    related_name="qualified_refs",
                ),
            },
        )

    def test_qualified_string_ref_to_different_app_requires_namespace(self) -> None:
        """A bare related_name on a qualified string FK to a different app should raise."""
        with pytest.raises(ValueError, match="related_name='bad_rel'.*SDK model"):
            type(
                "CrossAppStringRefModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "CrossAppStringRefModel",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "sdk_ref": models.ForeignKey(
                        "v1.Patient",
                        on_delete=models.DO_NOTHING,
                        related_name="bad_rel",
                    ),
                },
            )

    def test_error_message_includes_fix_suggestion(self) -> None:
        """The error message should suggest the namespaced form."""
        with pytest.raises(ValueError, match=r"%\(app_label\)s_my_rel"):
            type(
                "BadModel2",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "BadModel2",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "sdk_ref": models.ForeignKey(
                        SDKModel, on_delete=models.DO_NOTHING, related_name="my_rel"
                    ),
                },
            )


# ===========================================================================
# Tests for proxy model related_name scoping
# ===========================================================================


class TestProxyRelatedNameScoping:
    """Tests demonstrating how Django scopes reverse relations on proxy models.

    When a CustomModel FK targets a specific proxy (SDKModelProxy), Django
    installs the reverse descriptor on the concrete parent (SDKModel). Python
    MRO means ALL proxies of that base inherit the descriptor as an attribute.

    However, the FK's ``related_model`` is the specific proxy class, so:
    - The FK explicitly records which proxy it targets.
    - Two plugins with different proxies of the same SDK model can each
      declare bare related_names without colliding, because each FK targets
      a distinct proxy class.
    """

    def test_fk_related_model_is_the_targeted_proxy_not_sibling(self) -> None:
        """The FK's related_model should be the specific proxy, not the base or sibling."""
        fk = AttachedToProxyA._meta.get_field("proxy_a_ref")
        assert fk.related_model is SDKModelProxy
        assert fk.related_model is not SDKModelProxyB
        assert fk.related_model is not SDKModel

    def test_descriptor_inherited_by_sibling_proxy_via_mro(self) -> None:
        """Django installs the reverse descriptor on the concrete parent, so all
        proxies inherit it through Python's MRO. This is expected Django behavior —
        proxy models share their parent's class namespace.
        """
        assert hasattr(SDKModelProxy, "attached_records")
        # Sibling also sees it — this is Python inheritance, not a bug.
        assert hasattr(SDKModelProxyB, "attached_records")
        assert hasattr(SDKModel, "attached_records")

    def test_two_plugins_can_use_same_related_name_on_different_proxies(self) -> None:
        """Two plugins targeting different proxies of the same base can use the same
        bare related_name without the metaclass raising, because each proxy is a
        distinct class and therefore a distinct FK target.
        """
        # Plugin A's proxy + CustomModel
        PluginAProxy = type(
            "PluginAProxy",
            (SDKModel, ModelExtension),
            {
                "__module__": "plugin_a.models",
                "__qualname__": "PluginAProxy",
                "Meta": type("Meta", (), {"app_label": "plugin_a", "proxy": True}),
            },
        )
        PluginAModel = type(
            "PluginAModel",
            (CustomModel,),
            {
                "__module__": "plugin_a.models",
                "__qualname__": "PluginAModel",
                "sdk_ref": models.ForeignKey(
                    PluginAProxy, on_delete=models.DO_NOTHING, related_name="custom_records"
                ),
            },
        )

        # Plugin B's proxy + CustomModel with the SAME related_name — no collision
        PluginBProxy = type(
            "PluginBProxy",
            (SDKModel, ModelExtension),
            {
                "__module__": "plugin_b.models",
                "__qualname__": "PluginBProxy",
                "Meta": type("Meta", (), {"app_label": "plugin_b", "proxy": True}),
            },
        )
        PluginBModel = type(
            "PluginBModel",
            (CustomModel,),
            {
                "__module__": "plugin_b.models",
                "__qualname__": "PluginBModel",
                "sdk_ref": models.ForeignKey(
                    PluginBProxy, on_delete=models.DO_NOTHING, related_name="custom_records"
                ),
            },
        )

        # Both FK fields target distinct proxy classes
        fk_a = cast(models.Model, PluginAModel)._meta.get_field("sdk_ref")
        fk_b = cast(models.Model, PluginBModel)._meta.get_field("sdk_ref")
        assert fk_a.related_model is PluginAProxy
        assert fk_b.related_model is PluginBProxy
        assert fk_a.related_model is not fk_b.related_model


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
