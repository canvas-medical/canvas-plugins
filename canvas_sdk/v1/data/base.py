from typing import TYPE_CHECKING, Type

from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from canvas_sdk.value_set.value_set import ValueSet


class CommittableModelManager(models.Manager):
    def get_queryset(self) -> "models.QuerySet":
        # TODO: Should we just filter these out at the view level?
        return super().get_queryset().filter(deleted=False)

    def committed(self) -> "models.QuerySet":
        # The committer_id IS set, and the entered_in_error_id IS NOT set
        return self.filter(committer_id__isnull=False, entered_in_error_id__isnull=True)

    def for_patient(self, patient_id: str) -> "models.QuerySet":
        return self.filter(patient__id=patient_id)


class ValueSetLookupQuerySet(models.QuerySet):
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
        values_dict = value_set.values
        uri_codes = [
            (i[1], values_dict[i[0]])
            for i in value_set.CODE_SYSTEM_MAPPING.items()
            if i[0] in values_dict
        ]
        q_filter = Q()
        for system, codes in uri_codes:
            q_filter |= Q(codings__system=system, codings__code__in=codes)
        return self.filter(q_filter).distinct()
