from abc import abstractmethod
from collections.abc import Container
from typing import TYPE_CHECKING, Any, Protocol, Self, cast

from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from canvas_sdk.protocols.timeframe import Timeframe
    from canvas_sdk.value_set.value_set import ValueSet


class BaseModelManager(models.Manager):
    """A base manager for models."""

    def get_queryset(self) -> models.QuerySet:
        """Return a queryset that filters out deleted objects."""
        return super().get_queryset().filter(deleted=False)


class BaseQuerySet(models.QuerySet):
    """A base QuerySet inherited from Django's model.Queryset."""

    pass


class QuerySetProtocol(Protocol):
    """A typing protocol for use in mixins into models.QuerySet-inherited classes."""

    def filter(self, *args: Any, **kwargs: Any) -> Self:
        """Django's models.QuerySet filter method."""
        ...

    def distinct(self) -> Self:
        """Django's models.QuerySet distinct method."""
        ...


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


class CommittableQuerySet(BaseQuerySet, CommittableQuerySetMixin):
    """A queryset for committable objects."""

    pass


class ValueSetLookupQuerySet(BaseQuerySet, ValueSetLookupQuerySetMixin):
    """A class that includes methods for looking up value sets."""

    pass


class ValueSetLookupByNameQuerySet(BaseQuerySet, ValueSetLookupByNameQuerySetMixin):
    """A class that includes methods for looking up value sets by name."""

    pass


class ValueSetTimeframeLookupQuerySet(ValueSetLookupQuerySet, TimeframeLookupQuerySetMixin):
    """A class that includes methods for looking up value sets and using timeframes."""

    pass


__exports__ = ()
