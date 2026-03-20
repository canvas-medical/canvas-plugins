import json
import uuid
from abc import abstractmethod
from collections.abc import Container
from typing import TYPE_CHECKING, Any, Protocol, Self, cast

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models
from django.db.models import ForeignKey, OneToOneField, Q
from django.db.models.base import ModelBase
from django.db.models.constraints import UniqueConstraint

if TYPE_CHECKING:
    from canvas_sdk.protocols.timeframe import Timeframe
    from canvas_sdk.value_set.value_set import ValueSet

IS_SQLITE = connection.vendor == "sqlite"

MAX_FIELD_SIZE = 1_048_576  # 1 MB
MAX_BULK_SIZE = 10_000


class BulkOperationTooLarge(ValueError):
    """Raised when a bulk operation exceeds the maximum allowed size."""

    pass


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


class FieldValueTooLarge(ValueError):
    """Raised when a field value exceeds the maximum allowed size."""

    pass


def _check_write_permission() -> None:
    """Check if write operations are allowed in the current plugin context.

    Raises:
        NamespaceWriteDenied: If in a namespace context with read-only access.
    """
    from canvas_sdk.v1.plugin_database_context import get_current_schema, is_write_allowed

    schema = get_current_schema()
    if schema is None:
        return

    if not is_write_allowed():
        raise NamespaceWriteDenied(
            f"Write operation denied: namespace '{schema}' is read-only. "
            f"Plugin must declare 'read_write' access to perform write operations."
        )


class Model(models.Model, metaclass=ModelMetaclass):
    """A base model."""

    class Meta:
        abstract = True

    dbid = models.BigAutoField(primary_key=True)

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

        # Only OneToOneField may declare primary_key=True, which replaces
        # the inherited dbid. Reject primary_key=True on all other fields.
        suppress_dbid = False
        for key, value in attrs.items():
            if not isinstance(value, models.Field) or not getattr(value, "primary_key", False):
                continue
            if isinstance(value, OneToOneField):
                suppress_dbid = True
            elif isinstance(value, ForeignKey):
                raise ValueError(
                    f"CustomModel '{name}' sets primary_key=True on ForeignKey '{key}'. "
                    f"Use a OneToOneField instead."
                )
            else:
                raise ValueError(
                    f"CustomModel '{name}' sets primary_key=True on field '{key}'. "
                    f"CustomModels use an auto-generated primary key. "
                    f"To extend another model, use a OneToOneField with primary_key=True."
                )
        if suppress_dbid and "dbid" not in attrs:
            attrs["dbid"] = None

        # Snapshot developer-declared indexes/constraints before we auto-add FK indexes.
        developer_indexes = list(getattr(meta, "indexes", []))
        developer_constraints = list(getattr(meta, "constraints", []))

        # Look for foreign keys and one to one fields. Validate related_name and index them.
        auto_indexed_columns: set[str] = set()
        for key, value in attrs.items():
            if isinstance(value, (ForeignKey, OneToOneField)):
                # Reject non-namespaced related_name on FK/OneToOne fields that
                # target SDK models. SDK models are shared across plugins, so an
                # unqualified related_name like "status" would collide if two
                # plugins chose the same name. Plugin-private targets (CustomModels
                # and proxy models) don't need namespacing — each plugin's proxy
                # has its own app_label, so reverse relations are scoped to the
                # proxy class, not the shared concrete base.
                rel_name = value.remote_field.related_name
                target = value.remote_field.model
                if isinstance(target, str):
                    # At metaclass time, string FK references are not yet
                    # resolved.  Unqualified names and "self" resolve within
                    # the same app, which is always plugin-private.
                    target_is_plugin_private = (  # type: ignore[unreachable]
                        target == "self"
                        or "." not in target
                        or target.startswith(f"{meta.app_label}.")
                    )
                else:
                    target_is_plugin_private = isinstance(target, type) and (
                        issubclass(target, CustomModel)
                        or getattr(getattr(target, "_meta", None), "proxy", False)
                    )
                app_label = meta.app_label
                is_namespaced = rel_name and (
                    "%(app_label)s" in rel_name or rel_name.startswith(f"{app_label}_")
                )
                if (
                    rel_name
                    and rel_name != "+"
                    and not is_namespaced
                    and not target_is_plugin_private
                ):
                    target_name = target.__name__ if isinstance(target, type) else target
                    raise ValueError(
                        f"CustomModel '{name}' declares related_name='{rel_name}' "
                        f"on field '{key}' targeting SDK model '{target_name}'. "
                        f"To prevent collisions across plugins, use a namespaced "
                        f"related_name like related_name='%(app_label)s_{rel_name}', "
                        f"or related_name='+' to disable the reverse relation."
                    )

                # Auto-index (skip PK fields — they are already indexed)
                if not getattr(value, "primary_key", False):
                    if not hasattr(meta, "indexes"):
                        meta.indexes = []
                    column_name = f"{key}_id"
                    idx = models.Index(fields=[column_name])
                    if idx not in meta.indexes:
                        meta.indexes.append(idx)
                    auto_indexed_columns.add(column_name)
                    # Also track the field name so we catch both "room" and
                    # "room_id" style declarations.
                    auto_indexed_columns.add(key)

        # Reject developer-declared indexes or constraints that duplicate an
        # auto-indexed FK/OneToOne column.  These indexes are created
        # automatically — a duplicate wastes space and confuses readers.
        for idx in developer_indexes:
            if idx.fields and len(idx.fields) == 1:
                field_ref = idx.fields[0].lstrip("-")
                if field_ref in auto_indexed_columns:
                    raise ValueError(
                        f"CustomModel '{name}' declares an explicit index on "
                        f"'{idx.fields[0]}' in Meta.indexes. ForeignKey and "
                        f"OneToOneField columns are indexed automatically — "
                        f"remove the duplicate."
                    )
        for constraint in developer_constraints:
            if (
                isinstance(constraint, UniqueConstraint)
                and constraint.fields
                and len(constraint.fields) == 1
                and constraint.fields[0] in auto_indexed_columns
            ):
                raise ValueError(
                    f"CustomModel '{name}' declares a UniqueConstraint on "
                    f"'{constraint.fields[0]}' in Meta.constraints. "
                    f"OneToOneField columns already have a unique index — "
                    f"remove the duplicate."
                )

        # Require an explicit ``through`` model on ManyToManyFields.
        # Without one, Django auto-generates a bridge table whose name
        # won't match the plugin's schema, causing deployment failures.
        for key, value in attrs.items():
            if isinstance(value, models.ManyToManyField) and not value.remote_field.through:
                raise ValueError(
                    f"CustomModel '{name}' declares ManyToManyField '{key}' without "
                    f"an explicit 'through' model. Define a through model as a "
                    f"CustomModel and pass it via through='YourThroughModel'."
                )

        # Reject unique=True on individual fields. Developers should use
        # UniqueConstraint in Meta.constraints instead, because our DDL pipeline
        # cannot retroactively add UNIQUE to an existing column — it would
        # silently do nothing, leaving developers confused.
        # Skip relationship fields (OneToOneField inherently sets unique=True)
        # and primary keys.
        for key, value in attrs.items():
            if (
                isinstance(value, models.Field)
                and not isinstance(value, (ForeignKey, OneToOneField))
                and getattr(value, "unique", False)
                and not getattr(value, "primary_key", False)
            ):
                raise ValueError(
                    f"CustomModel '{name}' sets unique=True on field '{key}'. "
                    f"Use a UniqueConstraint in Meta.constraints instead:\n\n"
                    f"    class Meta:\n"
                    f"        constraints = [\n"
                    f"            models.UniqueConstraint(fields=['{key}'], name='uq_{key}'),\n"
                    f"        ]"
                )

        # Catch UniqueConstraint placed in Meta.indexes instead of Meta.constraints.
        # They're duck-type compatible with Index so Django doesn't complain, but
        # our DDL pipeline would silently create a non-unique index.
        indexes = getattr(meta, "indexes", None)
        if indexes:
            for idx in indexes:
                if isinstance(idx, UniqueConstraint):
                    raise ValueError(
                        f"CustomModel '{name}' places a UniqueConstraint in Meta.indexes. "
                        f"Move it to Meta.constraints instead."
                    )

        # Validate that Meta.constraints only contains UniqueConstraint instances
        # with simple field references (no descending ordering, no expressions).
        constraints = getattr(meta, "constraints", None)
        if constraints:
            for constraint in constraints:
                if not isinstance(constraint, UniqueConstraint):
                    raise ValueError(
                        f"CustomModel '{name}' declares a {type(constraint).__name__} "
                        f"in Meta.constraints. Only UniqueConstraint is supported."
                    )
                for field_name in constraint.fields:
                    if field_name.startswith("-"):
                        raise ValueError(
                            f"CustomModel '{name}' uses descending order '-{field_name[1:]}' "
                            f"in UniqueConstraint '{constraint.name}'. "
                            f"Sort order has no effect on uniqueness — use '{field_name[1:]}' instead."
                        )

        new_class = cast(type["Model"], super().__new__(cls, name, bases, attrs, **kwargs))

        return new_class


class CustomModel(Model, metaclass=CustomModelMetaclass):
    """A base model for custom normalized tables."""

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the model instance, checking write permissions and field sizes first."""
        self._check_write_permission()
        self._check_field_sizes()
        return super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Delete the model instance, checking write permissions first."""
        self._check_write_permission()
        return super().delete(*args, **kwargs)

    def _check_field_sizes(self) -> None:
        """Check that TextField and JSONField values do not exceed the size limit.

        Raises:
            FieldValueTooLarge: If any field value exceeds MAX_FIELD_SIZE.
        """
        for field in self._meta.local_fields:
            if isinstance(field, (models.TextField, models.JSONField)):
                value = getattr(self, field.attname, None)
                if value is None:
                    continue
                size = len(json.dumps(value)) if isinstance(field, models.JSONField) else len(value)
                if size > MAX_FIELD_SIZE:
                    raise FieldValueTooLarge(
                        f"Field '{field.name}' on {type(self).__name__} has size "
                        f"{size:,} bytes, exceeding the {MAX_FIELD_SIZE:,} character limit."
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

        return new_class


class ModelExtension(models.Model, metaclass=ModelExtensionMetaClass):
    """Mixin for proxy construction in plugin models."""

    class Meta:
        abstract = True


class proxy_field:
    """Descriptor that returns a ModelExtension proxy from a FK field.

    When a plugin defines a proxy model like ``CustomPatient(Patient, ModelExtension)``,
    accessing a ForeignKey that returns ``Patient`` can be wrapped with ``proxy_field``
    to transparently return ``CustomPatient`` instead::

        class CustomNote(Note, ModelExtension):
            patient = proxy_field(CustomPatient)

        note = CustomNote.objects.get(id=note_id)
        note.patient  # returns CustomPatient instance
    """

    def __init__(self, proxy_class: type) -> None:
        self.proxy_class = proxy_class
        self._parent_descriptor: Any = None

    def __set_name__(self, owner: type, name: str) -> None:
        for base in owner.__mro__[1:]:
            if name in base.__dict__:
                self._parent_descriptor = base.__dict__[name]
                break
        else:
            raise AttributeError(
                f"proxy_field '{name}' on {owner.__name__} could not find a "
                f"parent descriptor named '{name}' in any base class. "
                f"Ensure the base model defines a field with this name."
            )

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        result = self._parent_descriptor.__get__(obj, objtype)
        if result is not None:
            result.__class__ = self.proxy_class
        return result

    def __set__(self, obj: Any, value: Any) -> None:
        self._parent_descriptor.__set__(obj, value)


__exports__ = (
    "BulkOperationTooLarge",
    "CustomModel",
    "FieldValueTooLarge",
    "MAX_BULK_SIZE",
    "MAX_FIELD_SIZE",
    "ModelExtension",
    "NamespaceWriteDenied",
    "proxy_field",
)
