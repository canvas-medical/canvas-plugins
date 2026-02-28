import uuid
from abc import abstractmethod
from collections.abc import Container
from typing import TYPE_CHECKING, Any, Protocol, Self, cast

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models
from django.db.models import ForeignKey, OneToOneField, Q
from django.db.models.base import ModelBase
from django.utils.functional import cached_property

if TYPE_CHECKING:
    from django.contrib.contenttypes.fields import GenericRelation

    from canvas_sdk.protocols.timeframe import Timeframe
    from canvas_sdk.v1.data.custom_attribute import CustomAttribute
    from canvas_sdk.value_set.value_set import ValueSet

IS_SQLITE = connection.vendor == "sqlite"


class ModelMetaclass(ModelBase):
    """A metaclass for configuring data models."""

    def __new__(cls, name: str, bases: tuple, attrs: dict[str, Any], **kwargs: Any) -> type:
        """Create a new model class."""
        meta: Any = attrs.get("Meta")

        for field_name, field in list(attrs.items()):
            if isinstance(field, ArrayField) and IS_SQLITE:
                # Replace ArrayField(CharField(...)) with JSONField
                attrs[field_name] = models.JSONField(default=list)

        # set managed to True if database is SQLite and not explicitly set
        if meta and not hasattr(meta, "managed") and not getattr(meta, "abstract", False):
            meta.managed = IS_SQLITE

        new_class = cast(type["Model"], super().__new__(cls, name, bases, attrs, **kwargs))

        return new_class


class NamespaceWriteDenied(Exception):
    """Raised when a write operation is attempted without write access."""

    pass


class Model(models.Model, metaclass=ModelMetaclass):
    """A base model."""

    class Meta:
        abstract = True

    dbid = models.BigAutoField(primary_key=True)


class CustomModelMetaclass(ModelMetaclass):
    """A metaclass for configuring data models."""

    def __new__(cls, name: str, bases: tuple, attrs: dict[str, Any], **kwargs: Any) -> type:
        """Initialize the Meta class for the CustomModel to set critical info like app_label and db_table."""
        meta: Any = attrs.get("Meta")
        if meta is None:
            meta = type("Meta", (), {})
            attrs["Meta"] = meta

        # Set dynamic attributes
        meta.db_table = attrs["__qualname__"].lower()
        meta.app_label = attrs["__module__"].split(".")[0]

        # Look for foreign keys and one to one fields. Index them.
        for key, value in attrs.items():
            if isinstance(value, (ForeignKey, OneToOneField)):
                if not hasattr(meta, "indexes"):
                    meta.indexes = []
                idx = models.Index(fields=[f"{key}_id"])
                if idx not in meta.indexes:
                    meta.indexes.append(idx)

        new_class = cast(type["Model"], super().__new__(cls, name, bases, attrs, **kwargs))

        return new_class


class CustomModel(Model, metaclass=CustomModelMetaclass):
    """A base model for custom normalized tables."""

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the model instance, checking write permissions first."""
        self._check_write_permission()
        return super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Delete the model instance, checking write permissions first."""
        self._check_write_permission()
        return super().delete(*args, **kwargs)

    def _check_write_permission(self) -> None:
        """Check if write operations are allowed in the current context.

        Raises:
            NamespaceWriteDenied: If in a namespace context with read-only access.
        """
        from canvas_sdk.v1.plugin_database_context import get_current_schema, is_write_allowed

        schema = get_current_schema()
        if schema is None:
            # Not in a plugin context, allow write
            return

        if not is_write_allowed():
            raise NamespaceWriteDenied(
                f"Write operation denied: namespace '{schema}' is read-only. "
                f"Plugin must declare 'read_write' access to perform write operations."
            )


class IdentifiableModel(Model):
    """A model that includes an identifier."""

    class Meta:
        abstract = True

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class TimestampedModel(Model):
    """A model that includes created and modified timestamps."""

    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class AuditedModel(TimestampedModel):
    """A model that includes auditing fields."""

    class Meta:
        abstract = True

    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField(default=False)


class BaseModelManager(models.Manager):
    """A base manager for models."""

    def get_queryset(self) -> models.QuerySet:
        """Return a queryset that filters out deleted objects."""
        return super().get_queryset().filter(deleted=False)


class BaseQuerySet(models.QuerySet):
    """A base QuerySet inherited from Django's model.Queryset."""

    pass


if TYPE_CHECKING:
    # For type checking: Define the Protocol with method signatures
    class QuerySetProtocol(Protocol):
        """A typing protocol for use in mixins into models.QuerySet-inherited classes."""

        def filter(self, *args: Any, **kwargs: Any) -> Self:
            """Django's models.QuerySet filter method."""
            ...

        def distinct(self) -> Self:
            """Django's models.QuerySet distinct method."""
            ...
else:
    # At runtime: Empty class that doesn't shadow Django's methods
    class QuerySetProtocol:
        """A typing protocol for use in mixins into models.QuerySet-inherited classes.

        This Protocol is intentionally empty at runtime to avoid shadowing Django's
        QuerySet methods in the MRO. The method signatures are only defined when
        type checking (see TYPE_CHECKING block above).
        """


class ValueSetLookupQuerySetProtocol(QuerySetProtocol):
    """A typing protocol for use in mixins using value set lookup methods."""

    @staticmethod
    @abstractmethod
    def codings(value_set: type["ValueSet"]) -> tuple[tuple[str, set[str]]]:
        """A protocol method for defining codings."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def q_object(system: str, codes: Container[str]) -> Q:
        """A protocol method for defining Q objects for value set lookups."""
        raise NotImplementedError


class CommittableQuerySetMixin(QuerySetProtocol):
    """A queryset for committable objects."""

    def committed(self) -> Self:
        """Return a queryset that filters for objects that have been committed."""
        return self.filter(committer_id__isnull=False, entered_in_error_id__isnull=True)


class ForPatientQuerySetMixin(QuerySetProtocol):
    """A queryset for patient assets."""

    def for_patient(self, patient_id: str) -> Self:
        """Return a queryset that filters objects for a specific patient."""
        return self.filter(patient__id=patient_id)


class ValueSetLookupQuerySetMixin(ValueSetLookupQuerySetProtocol):
    """A QuerySet mixin that can filter objects based on a ValueSet."""

    def find(self, value_set: type["ValueSet"]) -> Self:
        """
        Filters conditions, medications, etc. to those found in the inherited ValueSet class that is passed.

        For example:

        from canvas_sdk.v1.data.condition import Condition
        from canvas_sdk.value_set.v2022.condition import MorbidObesity
        morbid_obesity_conditions = Condition.objects.find(MorbidObesity)

        This method can also be chained like so:

        Condition.objects.find(MorbidObesity).find(AnaphylacticReactionToCommonBakersYeast)
        """
        q_filter = Q()
        for system, codes in self.codings(value_set):
            q_filter |= self.q_object(system, codes)
        return self.filter(q_filter).distinct()

    @staticmethod
    def codings(value_set: type["ValueSet"]) -> tuple[tuple[str, set[str]]]:
        """Provide a sequence of tuples where each tuple is a code system URL and a set of codes."""
        values_dict = cast(dict, value_set.values)
        return cast(
            tuple[tuple[str, set[str]]],
            tuple(
                (i[1], values_dict[i[0]])
                for i in value_set.CODE_SYSTEM_MAPPING.items()
                if i[0] in values_dict
            ),
        )

    @staticmethod
    def q_object(system: str, codes: Container[str]) -> Q:
        """
        This method can be overridden if a Q object with different filtering options is needed.
        """
        return Q(codings__system=system, codings__code__in=codes)


class ValueSetLookupByNameQuerySetMixin(ValueSetLookupQuerySetMixin):
    """
    QuerySet for ValueSet lookups using code system name rather than URL.

    Some models, like Questionnaire, store the code system by name (e.g. "LOINC") rather than by the
    url (e.g. "http://loinc.org"). This subclass accommodates these models.
    """

    @staticmethod
    def codings(value_set: type["ValueSet"]) -> tuple[tuple[str, set[str]]]:
        """
        Provide a sequence of tuples where each tuple is a code system name and a set of codes.
        """
        values_dict = cast(dict, value_set.values)
        return cast(
            tuple[tuple[str, set[str]]],
            tuple(
                (i[0], values_dict[i[0]])
                for i in value_set.CODE_SYSTEM_MAPPING.items()
                if i[0] in values_dict
            ),
        )


class TimeframeLookupQuerySetProtocol(QuerySetProtocol):
    """A typing protocol for use in TimeframeLookupQuerySetMixin."""

    @property
    @abstractmethod
    def timeframe_filter_field(self) -> str:
        """A protocol method for timeframe_filter_field."""
        raise NotImplementedError


class TimeframeLookupQuerySetMixin(TimeframeLookupQuerySetProtocol):
    """A class that adds queryset functionality to filter using timeframes."""

    @property
    def timeframe_filter_field(self) -> str:
        """Returns the field that should be filtered on. Can be overridden for different models."""
        return "note__datetime_of_service"

    def within(self, timeframe: "Timeframe") -> Self:
        """A method to filter a queryset for datetimes within a timeframe."""
        return self.filter(
            **{
                f"{self.timeframe_filter_field}__range": (
                    timeframe.start.datetime,
                    timeframe.end.datetime,
                )
            }
        )


class CommittableQuerySet(CommittableQuerySetMixin, BaseQuerySet):
    """A queryset for committable objects."""

    pass


class ValueSetLookupQuerySet(ValueSetLookupQuerySetMixin, BaseQuerySet):
    """A class that includes methods for looking up value sets."""

    pass


class ValueSetLookupByNameQuerySet(ValueSetLookupByNameQuerySetMixin, BaseQuerySet):
    """A class that includes methods for looking up value sets by name."""

    pass


class ValueSetTimeframeLookupQuerySet(TimeframeLookupQuerySetMixin, ValueSetLookupQuerySet):
    """A class that includes methods for looking up value sets and using timeframes."""

    pass


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
            from .custom_attribute import CustomAttributeAwareManager

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

    if TYPE_CHECKING:
        custom_attributes: GenericRelation

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Add a GenericRelation to custom_attributes on each subclass."""
        super().__init_subclass__(**kwargs)

        from django.contrib.contenttypes.fields import GenericRelation

        from .custom_attribute import CustomAttribute

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
        from .custom_attribute import CustomAttribute

        if not hasattr(self, "custom_attributes"):
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'custom_attributes' GenericRelation field"
            )

        if (
            hasattr(self, "_prefetched_objects_cache")
            and "custom_attributes" in self._prefetched_objects_cache
        ):
            # Use prefetched data first
            for attr in self.custom_attributes.all():
                if attr.name == name:
                    return attr.value
            # Attribute not in prefetch cache — fall back to DB so that
            # with_only() doesn't silently return None for attributes that
            # exist but weren't prefetched.

        # Fall back to database query
        try:
            attr = CustomAttribute.objects.get(
                content_type_id=self._content_type_id, object_id=self.pk, name=name
            )
            return attr.value
        except CustomAttribute.DoesNotExist:
            return None

    def set_attribute(self, name: str, value: Any) -> "CustomAttribute":
        """Set a custom attribute value."""
        from .custom_attribute import CustomAttribute

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

    def set_attributes(self, attributes: dict[str, Any]) -> list["CustomAttribute"]:
        """Set multiple custom attributes using bulk operations.

        Uses INSERT ... ON CONFLICT DO UPDATE (upsert) to atomically create or
        update attributes, avoiding race conditions under concurrent writes.
        """
        from .custom_attribute import VALUE_FIELDS, CustomAttribute

        if not hasattr(self, "custom_attributes"):
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'custom_attributes' GenericRelation field"
            )

        if not attributes:
            return []

        attrs = []
        for name, value in attributes.items():
            attr = CustomAttribute(
                content_type_id=self._content_type_id, object_id=self.pk, name=name
            )
            attr.value = value
            attrs.append(attr)

        # Atomic upsert: INSERT ... ON CONFLICT (content_type, object_id, name) DO UPDATE
        return CustomAttribute.objects.bulk_create(
            attrs,
            update_conflicts=True,
            unique_fields=["content_type", "object_id", "name"],
            update_fields=list(VALUE_FIELDS),
        )

    def delete_attribute(self, name: str) -> bool:
        """Delete a custom attribute by name. Returns True if deleted, False if not found."""
        from .custom_attribute import CustomAttribute

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


__exports__ = ("CustomModel", "ModelExtension", "NamespaceWriteDenied")
