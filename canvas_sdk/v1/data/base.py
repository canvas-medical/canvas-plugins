from django.db import models


class CommittableModelManager(models.Manager):
    def get_queryset(self) -> "models.QuerySet":
        # TODO: Should we just filter these out at the view level?
        return super().get_queryset().filter(deleted=False)

    def committed(self) -> "models.QuerySet":
        # The committer_id IS set, and the entered_in_error_id IS NOT set
        return self.filter(committer_id__isnull=False, entered_in_error_id__isnull=True)

    def for_patient(self, patient_id: str) -> "models.QuerySet":
        return self.filter(patient__id=patient_id)
