from canvas_sdk.effects import Effect
from canvas_sdk.effects.task import AddTask, TaskStatus
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data import Prescription, Task, Team
from canvas_sdk.v1.data.task import TaskPriority
from canvas_sdk.v1.data.team import TeamResponsibility
from logger import log


class CreateRefillTaskHandler(BaseHandler):
    """
    Creates a follow-up task when a refill prescription is queued for transmission.

    Listens for PRESCRIPTION_PENDING. This fires after Sign / Sign & Send queues the rx,
    regardless of which UI button the user clicked. Only refills produce a follow-up
    task; original prescriptions are ignored.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.PRESCRIPTION_PENDING),
    ]

    def compute(self) -> list[Effect]:
        """Create a follow-up task when a refill prescription is queued for transmission."""
        log.info(f"Creating refill task for {self.event.target.id}")

        prescription = Prescription.objects.filter(id=self.event.target.id).first()
        if not prescription:
            log.info(f"PRESCRIPTION_PENDING: prescription {self.event.target.id} not found")
            return []

        if not prescription.is_refill:
            return []

        medication = self._medication_name(prescription)
        title = f"Follow up on refill of {medication}"
        patient_id = self.context["patient"]["id"]

        # Prevent duplicate follow-up tasks for the same medication/patient.
        if Task.objects.filter(
            title=title, status=TaskStatus.OPEN.value, patient__id=patient_id
        ).exists():
            log.info(f"Refill follow-up task already exists for {medication}, skipping")
            return []

        team = (
            Team.objects.filter(
                responsibilities__contains=[TeamResponsibility.PROCESS_REFILL_REQUESTS.value]
            )
            .values_list("id", flat=True)
            .first()
        )

        log.info(f"Creating refill follow-up: '{title}' for patient {patient_id}, team {team}")
        return [
            AddTask(
                title=title,
                priority=TaskPriority.URGENT,
                patient_id=patient_id,
                team_id=str(team) if team else None,
            ).apply()
        ]

    def _medication_name(self, prescription: Prescription) -> str:
        """Return a human-readable medication name, falling back across fields."""
        return (
            getattr(prescription, "display_name", None)
            or getattr(prescription, "name", None)
            or "medication"
        )
