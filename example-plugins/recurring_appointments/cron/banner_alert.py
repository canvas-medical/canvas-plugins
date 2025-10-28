from datetime import datetime

from django.db.models import Q, Count

from canvas_sdk.effects import Effect
from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.handlers.cron_task import CronTask
from canvas_sdk.v1.data import Appointment


class CheckPatientAppointmentRecurrence(CronTask):
    """Every day at 3 AM, check for recurring appointments that only have <= 1 visit left and add a banner alert to the patient timeline."""

    SCHEDULE = "0 3 * * *"

    def execute(self) -> list[Effect]:
        """Get all recurring appointments that have == 1 visit left and add a banner alert to the patient timeline."""

        _filter = Q(children__start_time__gt=datetime.now()) & ~Q(children__status="cancelled")
        patients_to_add_banners = (
            Appointment.objects.filter(_filter)
            .annotate(future_appointments=Count("children", filter=_filter))
            .values_list("patient__id", flat=True)
            .filter(future_appointments=1)
            .distinct()
        )

        effects = []
        for patient in patients_to_add_banners:
            banner = AddBannerAlert(
                patient_id=patient,
                key="recurring-appointment-end-banner",
                narrative="Only 1 visit scheduled. Confirm future recurrence and schedule",
                placement=[
                    AddBannerAlert.Placement.TIMELINE,
                ],
                intent=AddBannerAlert.Intent.INFO,
            )
            effects.append(banner.apply())

        return effects
