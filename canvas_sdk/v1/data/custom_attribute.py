"""CustomAttribute model and related managers for flexible key-value storage.

CustomAttribute stores values across typed columns (``text_value``, ``int_value``,
``bool_value``, etc.) so that each value type is stored natively in the database.
A virtual ``value`` property and type-aware QuerySets allow transparent read/write
access without knowing which column a value lives in.
"""

import datetime
import decimal
import operator
from functools import reduce
from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Prefetch, Q

from .base import Model, ModelExtension

VALUE_FIELD_MAP: dict[type, str] = {
    bool: "bool_value",
    str: "text_value",
    int: "int_value",
    float: "decimal_value",
    decimal.Decimal: "decimal_value",
    datetime.datetime: "timestamp_value",
    datetime.date: "date_value",
    dict: "json_value",
    list: "json_value",
}

VALUE_FIELDS = tuple(dict.fromkeys(VALUE_FIELD_MAP.values()))


def _rewrite_value_lookups(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    match_key: str = "value",
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    """Rewrite ``value`` kwargs to the correct typed column.

    Args:
        args: Positional Q-object arguments from filter()/exclude().
        kwargs: Keyword arguments from filter()/exclude().
        match_key: The kwarg key (or prefix before ``__``) to intercept.
            Defaults to ``"value"`` for direct CustomAttribute queries.
            Use ``"custom_attributes__value"`` for cross-relation queries.

    Returns:
        A (args, kwargs) tuple with value lookups rewritten.
    """
    new_kwargs: dict[str, Any] = {}
    extra_q: list[Q] = []
    prefix_len = len(match_key)

    for key, val in kwargs.items():
        if key == match_key or key.startswith(f"{match_key}__"):
            suffix = key[prefix_len:]  # "" or "__gte" etc.
            target_prefix = match_key.rsplit("value", 1)[0]  # "" or "custom_attributes__"
            _rewrite_one(suffix, val, target_prefix, new_kwargs, extra_q)
        else:
            new_kwargs[key] = val

    return (*args, *extra_q), new_kwargs


def _rewrite_one(
    suffix: str,
    val: Any,
    target_prefix: str,
    new_kwargs: dict[str, Any],
    extra_q: list[Q],
) -> None:
    """Rewrite a single value lookup into typed column lookup(s)."""
    # value=None → all columns must be NULL
    if not suffix and val is None:
        for field in VALUE_FIELDS:
            new_kwargs[f"{target_prefix}{field}__isnull"] = True
        return

    # value__isnull
    if suffix == "__isnull":
        if val:
            for field in VALUE_FIELDS:
                new_kwargs[f"{target_prefix}{field}__isnull"] = True
        else:
            extra_q.append(
                reduce(
                    operator.or_,
                    (Q(**{f"{target_prefix}{f}__isnull": False}) for f in VALUE_FIELDS),
                )
            )
        return

    # value__in → all items must share a single type
    if suffix == "__in":
        types = {type(v) for v in val}
        if len(types) != 1:
            raise TypeError(
                "All values in a 'value__in' lookup must be the same type, got: "
                + ", ".join(t.__name__ for t in types)
            )
        val_type = types.pop()
    else:
        val_type = type(val)

    typed_field = VALUE_FIELD_MAP.get(val_type)
    if typed_field is None:
        raise TypeError(
            f"Cannot filter CustomAttribute.value by type '{val_type.__name__}'. "
            f"Use the specific column name (e.g., json_value) directly."
        )
    new_kwargs[f"{target_prefix}{typed_field}{suffix}"] = val


class CustomAttributeQuerySet(models.QuerySet):
    """QuerySet that rewrites ``value`` lookups to the correct typed column.

    Allows filtering by the virtual ``value`` property using the Python type of
    the right-hand side to select the database column::

        CustomAttribute.objects.filter(value="blue")       # → text_value="blue"
        CustomAttribute.objects.filter(value__gte=5)       # → int_value__gte=5
        CustomAttribute.objects.filter(value=None)         # → all columns NULL
        CustomAttribute.objects.filter(value__isnull=True) # → all columns NULL
    """

    def filter(self, *args: Any, **kwargs: Any) -> "CustomAttributeQuerySet":
        """Filter with automatic ``value`` → typed-column rewriting."""
        args, kwargs = _rewrite_value_lookups(args, kwargs)
        return super().filter(*args, **kwargs)

    def exclude(self, *args: Any, **kwargs: Any) -> "CustomAttributeQuerySet":
        """Exclude with automatic ``value`` → typed-column rewriting."""
        args, kwargs = _rewrite_value_lookups(args, kwargs)
        return super().exclude(*args, **kwargs)


CustomAttributeManager = models.Manager.from_queryset(CustomAttributeQuerySet)


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

    objects = CustomAttributeManager()

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
        for field in VALUE_FIELDS:
            setattr(self, field, None)

        if value is None:
            return

        typed_field = VALUE_FIELD_MAP.get(type(value))
        if typed_field is None:
            self.json_value = value
        else:
            setattr(self, typed_field, value)


class CustomAttributeAwareQuerySet(models.QuerySet):
    """QuerySet for models with custom attributes.

    Rewrites ``custom_attributes__value`` lookups to the correct typed column
    so that parent models can filter by attribute value across the join::

        AttributeHub.objects.filter(custom_attributes__value="blue")
        StaffProxy.objects.filter(custom_attributes__value__gte=5)
    """

    def filter(self, *args: Any, **kwargs: Any) -> "CustomAttributeAwareQuerySet":
        """Filter with automatic ``custom_attributes__value`` → typed-column rewriting."""
        args, kwargs = _rewrite_value_lookups(args, kwargs, match_key="custom_attributes__value")
        return super().filter(*args, **kwargs)

    def exclude(self, *args: Any, **kwargs: Any) -> "CustomAttributeAwareQuerySet":
        """Exclude with automatic ``custom_attributes__value`` → typed-column rewriting."""
        args, kwargs = _rewrite_value_lookups(args, kwargs, match_key="custom_attributes__value")
        return super().exclude(*args, **kwargs)


class CustomAttributeAwareManager(models.Manager):
    """Manager that automatically prefetches custom attributes and supports
    ``custom_attributes__value`` lookups across the join.
    """

    def get_queryset(self) -> CustomAttributeAwareQuerySet:
        """Prefetch all custom attributes for the queryset."""
        return CustomAttributeAwareQuerySet(self.model, using=self._db).prefetch_related(
            "custom_attributes"
        )

    def with_only(
        self, attribute_names: str | list[str] | None = None
    ) -> CustomAttributeAwareQuerySet:
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

    objects = CustomAttributeAwareManager()

    # Only id and type fields - all other data stored as custom attributes
    type = models.CharField(max_length=100)
    id = models.CharField(max_length=100)

    def __str__(self) -> str:
        """Return a human-readable representation of the hub."""
        return f"AttributeHub({self.type}): {self.id}"


__exports__ = (
    "CustomAttribute",
    "CustomAttributeQuerySet",
    "CustomAttributeAwareQuerySet",
    "CustomAttributeAwareManager",
    "AttributeHub",
    "VALUE_FIELD_MAP",
    "VALUE_FIELDS",
)
