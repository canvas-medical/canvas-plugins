import datetime
import decimal
from typing import Any, cast

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Prefetch
from django.utils.functional import cached_property

from .base import Model, ModelMetaclass


class CustomAttribute(Model):
    """
    A flexible attribute storage model that can be attached to any SDK model
    via GenericRelation. Supports multiple value types stored in separate columns.
    """

    class Meta:
        db_table = "custom_attribute"

        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "name"], name="unique_custom_attribute"
            )
        ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    name = models.TextField()

    # Value storage fields - only one should be populated per attribute
    text_value = models.TextField(null=True, blank=True)
    date_value = models.DateField(null=True, blank=True)
    timestamp_value = models.DateTimeField(null=True, blank=True)
    int_value = models.IntegerField(null=True, blank=True)
    decimal_value = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    bool_value = models.BooleanField(null=True, blank=True)
    json_value = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        """Return a human-readable representation of the attribute."""
        return f"{self.content_object} - {self.name}: {self.value}"

    @property
    def value(self) -> Any | None:
        """Return the actual value regardless of which field it's stored in."""
        if self.text_value is not None:
            return self.text_value
        elif self.date_value is not None:
            return self.date_value
        elif self.timestamp_value is not None:
            return self.timestamp_value
        elif self.int_value is not None:
            return self.int_value
        elif self.decimal_value is not None:
            return self.decimal_value
        elif self.bool_value is not None:
            return self.bool_value
        elif self.json_value is not None:
            return self.json_value
        return None

    @value.setter
    def value(self, value: Any) -> None:
        """Set the value in the appropriate field based on type."""
        # Clear all value fields first
        self.text_value = None
        self.date_value = None
        self.timestamp_value = None
        self.int_value = None
        self.decimal_value = None
        self.bool_value = None
        self.json_value = None

        # Set the appropriate field based on value type (exact type match, no inheritance)
        value_type = type(value)
        if value_type is bool:
            self.bool_value = value
        elif value_type is str:
            self.text_value = value
        elif value_type is int:
            self.int_value = value
        elif value_type in (float, decimal.Decimal):
            self.decimal_value = value
        elif value_type is datetime.datetime:
            self.timestamp_value = value
        elif value_type is datetime.date:
            self.date_value = value
        elif value is None:
            pass  # All fields already cleared
        else:
            # Store complex objects as JSON
            self.json_value = value


class CustomAttributeAwareManager(models.Manager):
    """Manager that automatically prefetches custom attributes."""

    def get_queryset(self) -> models.QuerySet:
        """Prefetch all custom attributes for the queryset."""
        return super().get_queryset().prefetch_related("custom_attributes")

    def with_only(self, attribute_names: str | list[str] | None = None) -> models.QuerySet:
        """Prefetch only specific custom attributes by name.

        attribute_names may be a single string or list of strings.
        If None, prefetches all attributes.
        """
        if attribute_names is None:
            return self.get_queryset()

        if isinstance(attribute_names, str):
            attribute_names = [attribute_names]

        # Clear default prefetch and replace with narrower one
        return (
            self.get_queryset()
            .prefetch_related(None)
            .prefetch_related(
                Prefetch(
                    "custom_attributes",
                    queryset=CustomAttribute.objects.filter(name__in=attribute_names),
                )
            )
        )


class ModelExtensionMetaClass(ModelMetaclass):
    """Metaclass that sets app_label and proxy for plugin proxy models."""

    def __new__(cls, name: str, bases: tuple, attrs: dict[str, Any], **kwargs: Any) -> type:
        """Create a new class, setting app_label and proxy from the module name for plugins."""
        meta: Any = attrs.get("Meta")
        if meta is None:
            meta = type("Meta", (), {})
            attrs["Meta"] = meta

        if not attrs["__module__"].startswith("canvas_sdk"):
            # set the app label for proxy models belonging to the plugin
            meta.app_label = attrs["__module__"].split(".")[0]

            # auto-set proxy if subclassing a concrete SDK model
            if not getattr(meta, "abstract", False) and getattr(meta, "proxy", None) is None:
                has_concrete_base = any(
                    hasattr(b, "_meta") and not b._meta.abstract
                    for b in bases
                    if b is not ModelExtension
                )
                if has_concrete_base:
                    meta.proxy = True

        new_class = cast(type["Model"], super().__new__(cls, name, bases, attrs, **kwargs))

        # Auto-assign the aware manager after Django's full class setup.
        # This must happen here (not in __init_subclass__) because Django's
        # proxy model machinery copies managers from the concrete parent
        # during ModelBase.__new__, which would overwrite any manager set
        # earlier in __init_subclass__.
        if not new_class.__module__.startswith("canvas_sdk") and "objects" not in attrs:
            new_class.add_to_class("objects", CustomAttributeAwareManager())

        return new_class


# Mixin for models that want custom attributes
class ModelExtension(models.Model, metaclass=ModelExtensionMetaClass):
    """
    Mixin to add custom attributes support to any SDK model.
    Automatically includes the GenericRelation field.
    """

    class Meta:
        abstract = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Add a GenericRelation to custom_attributes on each subclass."""
        super().__init_subclass__(**kwargs)

        cls.add_to_class(
            "custom_attributes",
            GenericRelation(
                CustomAttribute, content_type_field="content_type", object_id_field="object_id"
            ),
        )

    @cached_property
    def _content_type_id(self) -> int:
        """Cache the content type ID lookup for this model instance."""
        # For proxy models, use the content type of the base model
        base_model = self._meta.concrete_model
        assert base_model is not None
        app_label = base_model._meta.app_label
        model_name = base_model._meta.model_name

        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM django_content_type WHERE app_label = %s AND model = %s",
                [app_label, model_name],
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"ContentType not found for {app_label}.{model_name}")
            return row[0]

    def get_attribute(self, name: str) -> Any:
        """Get a custom attribute value by name."""
        if not hasattr(self, "custom_attributes"):
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'custom_attributes' GenericRelation field"
            )

        if (
            hasattr(self, "_prefetched_objects_cache")
            and "custom_attributes" in self._prefetched_objects_cache
        ):
            # Use prefetched data
            for attr in self.custom_attributes.all():
                if attr.name == name:
                    return attr.value
            return None
        else:
            # Fall back to database query
            try:
                attr = CustomAttribute.objects.get(
                    content_type_id=self._content_type_id, object_id=self.pk, name=name
                )
                return attr.value
            except CustomAttribute.DoesNotExist:
                return None

    def set_attribute(self, name: str, value: Any) -> CustomAttribute:
        """Set a custom attribute value."""
        if not hasattr(self, "custom_attributes"):
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'custom_attributes' GenericRelation field"
            )

        # Create custom attribute with cached content_type_id
        attr, created = CustomAttribute.objects.get_or_create(
            content_type_id=self._content_type_id, object_id=self.pk, name=name, defaults={}
        )
        attr.value = value  # Use the property setter
        attr.save()
        return attr

    def set_attributes(self, attributes: dict[str, Any]) -> list[CustomAttribute]:
        """Set multiple custom attributes using bulk operations."""
        if not hasattr(self, "custom_attributes"):
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'custom_attributes' GenericRelation field"
            )

        # Get existing attributes from prefetched data or database
        existing_attrs: dict[str, CustomAttribute] = {}
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "custom_attributes" in self._prefetched_objects_cache
        ):
            # Use prefetched data
            for attr in self.custom_attributes.all():
                existing_attrs[attr.name] = attr
        else:
            # Fall back to database query
            for attr in CustomAttribute.objects.filter(
                content_type_id=self._content_type_id, object_id=self.pk
            ):
                existing_attrs[attr.name] = attr

        # Separate attributes to create vs update
        to_create: list[CustomAttribute] = []
        to_update: list[CustomAttribute] = []

        for name, value in attributes.items():
            if name in existing_attrs:
                # Update existing attribute
                attr = existing_attrs[name]
                attr.value = value
                to_update.append(attr)
            else:
                # Create new attribute
                attr = CustomAttribute(
                    content_type_id=self._content_type_id, object_id=self.pk, name=name
                )
                attr.value = value
                to_create.append(attr)

        # Perform bulk operations
        created_attrs: list[CustomAttribute] = []
        if to_create:
            created_attrs = CustomAttribute.objects.bulk_create(to_create)

        if to_update:
            CustomAttribute.objects.bulk_update(
                to_update,
                [
                    "text_value",
                    "date_value",
                    "timestamp_value",
                    "int_value",
                    "decimal_value",
                    "bool_value",
                    "json_value",
                ],
            )

        return created_attrs + to_update

    def delete_attribute(self, name: str) -> bool:
        """Delete a custom attribute by name. Returns True if deleted, False if not found."""
        if not hasattr(self, "custom_attributes"):
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'custom_attributes' GenericRelation field"
            )

        try:
            CustomAttribute.objects.get(
                content_type_id=self._content_type_id, object_id=self.pk, name=name
            ).delete()
            return True
        except CustomAttribute.DoesNotExist:
            return False


class AttributeHub(Model, ModelExtension):
    """
    A simple model that serves only as a hub for custom attributes.
    Useful for storing arbitrary key-value data that doesn't belong to existing models.
    """

    class Meta:
        db_table = "attribute_hub"

    # Only id and type fields - all other data stored as custom attributes
    type = models.CharField(max_length=100)
    id = models.CharField(max_length=100)

    def __str__(self) -> str:
        """Return a human-readable representation of the hub."""
        return f"AttributeHub({self.type}): {self.id}"


__exports__ = (
    "CustomAttribute",
    "CustomAttributeAwareManager",
    "ModelExtension",
    "AttributeHub",
)
