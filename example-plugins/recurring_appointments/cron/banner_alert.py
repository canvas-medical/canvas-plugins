from canvas_sdk.effects import Effect
from canvas_sdk.handlers.cron_task import CronTask


class CheckPatientAppointmentRecurrence(CronTask):
    """Every day at 3 AM, check for recurring appointments that only have <= 1 visit left and add a banner alert to the patient timeline."""
    #SCHEDULE = "0 3 * * *"
    SCHEDULE = "* * * * *"

    def execute(self) -> list[Effect]:





       pass
