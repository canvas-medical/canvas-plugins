from collections.abc import Container
from typing import TYPE_CHECKING, Type, cast

from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from canvas_sdk.value_set.value_set import ValueSet


class CommittableModelManager(models.Manager):
    """A manager for commands that can be committed."""

    def get_queryset(self) -> "models.QuerySet":
        """Return a queryset that filters out deleted objects."""
        # TODO: Should we just filter these out at the view level?
        return super().get_queryset().filter(deleted=False)

    def committed(self) -> "models.QuerySet":
        """Return a queryset that filters for objects that have been committed."""
        # The committer_id IS set, and the entered_in_error_id IS NOT set
        return self.filter(committer_id__isnull=False, entered_in_error_id__isnull=True)

    def for_patient(self, patient_id: str) -> "models.QuerySet":
        """Return a queryset that filters objects for a specific patient."""
        return self.filter(patient__id=patient_id)


class ValueSetLookupQuerySet(models.QuerySet):
    """A QuerySet that can filter objects based on a ValueSet."""

    def find(self, value_set: Type["ValueSet"]) -> models.QuerySet:
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
    def codings(value_set: Type["ValueSet"]) -> tuple[tuple[str, set[str]]]:
        """Provide a sequence of tuples where each tuple is a code system URL and a set of codes."""
        values_dict = value_set.values
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


class ValueSetLookupByNameQuerySet(ValueSetLookupQuerySet):
    """
    QuerySet for ValueSet lookups using code system name rather than URL.

    Some models, like Questionnaire, store the code system by name (e.g. "LOINC") rather than by the
    url (e.g. "http://loinc.org"). This subclass accommodates these models.
    """

    @staticmethod
    def codings(value_set: Type["ValueSet"]) -> tuple[tuple[str, set[str]]]:
        """
        Provide a sequence of tuples where each tuple is a code system name and a set of codes.
        """
        values_dict = value_set.values
        return cast(
            tuple[tuple[str, set[str]]],
            tuple(
                (i[0], values_dict[i[0]])
                for i in value_set.CODE_SYSTEM_MAPPING.items()
                if i[0] in values_dict
            ),
        )
