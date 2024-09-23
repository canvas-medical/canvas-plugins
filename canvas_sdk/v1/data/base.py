from typing import TYPE_CHECKING, Type

from django.db import models
from django.db.models import Q

from canvas_sdk.value_set.constants import SYSTEM_CODE_URI_MAPPING

if TYPE_CHECKING:
    from canvas_sdk.value_set.value_set import ValueSet


class CommittableModelManager(models.Manager):
    def get_queryset(self) -> "models.QuerySet":
        # TODO: Should we just filter these out at the view level?
        return super().get_queryset().filter(deleted=False)

    def committed(self) -> "models.QuerySet":
        # The committer_id IS set, and the entered_in_error_id IS NOT set
        return self.filter(committer_id__isnull=False, entered_in_error_id__isnull=True)

    def for_patient_id(self, patient_id: str) -> "models.QuerySet":
        return self.filter(patient__id=patient_id)


class ValueSetLookupQuerySet(models.QuerySet):
    def in_value_set(
        self, value_set: Type["ValueSet"], code_system_mapping: dict[str, str] | None = None
    ) -> models.QuerySet:
        """
        Filters conditions, medications, etc. to those found in the inherited ValueSet class that is passed.

        For example:

        from canvas_sdk.v1.data.condition import Condition
        from canvas_sdk.value_set.v2022.condition import MorbidObesity
        morbid_obesity_conditions = Condition.objects.in_value_set(MorbidObesity)

        This method can also be chained like so:

        Condition.objects.in_value_set(MorbidObesity).in_value_set(AnaphylacticReactionToCommonBakersYeast)

        A code/system mapping dictionary can be optionally passed to define value_set codes and URI values
        so that plugin authors can use custom value sets.
        """

        if not code_system_mapping:
            code_system_mapping = SYSTEM_CODE_URI_MAPPING
        uri_codes = [
            (i[1], getattr(value_set, i[0]))
            for i in code_system_mapping.items()
            if hasattr(value_set, i[0])
        ]
        q_filter = Q()
        for system, codes in uri_codes:
            q_filter |= Q(codings__system=system, codings__code__in=codes)
        return self.filter(q_filter).distinct()
