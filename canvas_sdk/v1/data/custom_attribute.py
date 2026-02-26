import datetime
import decimal
from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Prefetch

from .base import Model, ModelExtension


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

        # Remove only the default "custom_attributes" prefetch, preserving any
        # others the programmer may have added, then add the filtered one.
        qs = self.get_queryset()
        qs._prefetch_related_lookups = tuple(  # type: ignore[attr-defined]
            lookup
            for lookup in qs._prefetch_related_lookups  # type: ignore[attr-defined]
            if (lookup if isinstance(lookup, str) else lookup.prefetch_to) != "custom_attributes"
        )
        return qs.prefetch_related(
            Prefetch(
                "custom_attributes",
                queryset=CustomAttribute.objects.filter(name__in=attribute_names),
            )
        )


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
    "AttributeHub",
)
