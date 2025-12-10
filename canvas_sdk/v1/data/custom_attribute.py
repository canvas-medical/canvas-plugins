import datetime
from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property


class CustomAttribute(models.Model):
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
    timestamp_value = models.DateTimeField(null=True, blank=True)
    int_value = models.IntegerField(null=True, blank=True)
    float_value = models.FloatField(null=True, blank=True)
    bool_value = models.BooleanField(null=True, blank=True)
    json_value = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.content_object} - {self.name}: {self.value}"

    @property
    def value(self) -> str | int | float | bool | dict | Any | None:
        """Return the actual value regardless of which field it's stored in."""
        if self.text_value is not None:
            return self.text_value
        elif self.timestamp_value is not None:
            return self.timestamp_value
        elif self.int_value is not None:
            return self.int_value
        elif self.float_value is not None:
            return self.float_value
        elif self.bool_value is not None:
            return self.bool_value
        elif self.json_value is not None:
            return self.json_value
        return None

    @value.setter
    def value(self, val: Any) -> None:
        """Set the value in the appropriate field based on type."""
        # Clear all value fields first
        self.text_value = None
        self.timestamp_value = None
        self.int_value = None
        self.float_value = None
        self.bool_value = None
        self.json_value = None

        # Set the appropriate field based on value type
        # Note: Check bool BEFORE int since bool is a subclass of int in Python
        if isinstance(val, bool):
            self.bool_value = val
        elif isinstance(val, str):
            self.text_value = val
        elif isinstance(val, int):
            self.int_value = val
        elif isinstance(val, float):
            self.float_value = val
        elif isinstance(val, datetime.datetime):
            self.timestamp_value = val
        elif val is None:
            pass  # All fields already cleared
        else:
            # Store complex objects as JSON
            self.json_value = val


# Mixin for models that want custom attributes
class CustomAttributeMixin(models.Model):
    """
    Mixin to add custom attributes support to any SDK model.
    Automatically includes the GenericRelation field.
    """

    class Meta:
        abstract = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Add GenericRelation to any class that inherits this mixin
        from django.contrib.contenttypes.fields import GenericRelation

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

    """
    Mixin to add custom attributes support to any SDK model.

    Usage:
        class MyModel(Model, CustomAttributeMixin):
            # ... your model fields ...

            # Add the GenericRelation
            custom_attributes = GenericRelation(
                CustomAttribute,
                content_type_field="content_type",
                object_id_field="object_id"
            )
    """

    def get_attribute(self, name: str) -> Any:
        """Get a custom attribute value by name."""
        if not hasattr(self, "custom_attributes"):
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'custom_attributes' GenericRelation field"
            )

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


__exports__ = ("CustomAttribute", "CustomAttributeMixin")
