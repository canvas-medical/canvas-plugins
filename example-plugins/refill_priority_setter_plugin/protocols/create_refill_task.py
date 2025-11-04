from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.task import TaskPriority
from canvas_sdk.effects.task import AddTask, TaskStatus
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Task, Team
from canvas_sdk.v1.data.team import TeamResponsibility
from logger import log


class CreateRefillTaskProtocol(BaseProtocol):
    """
    Protocol that automatically creates follow-up tasks when refill commands are committed.
    
    This protocol listens for REFILL_COMMAND__POST_COMMIT events and creates a follow-up
    task to ensure proper monitoring and completion of refill requests. The task is
    automatically assigned to a team with refill processing responsibilities.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.REFILL_COMMAND__POST_COMMIT),
    ]

    def compute(self) -> list[Effect]:
        """
        Creates a follow-up refill task when a refill command is committed.
        
        Business Logic:
        - Creates a task with title "Follow up on refill of {medication}"
        - Sets priority to URGENT for timely processing
        - Assigns to a team with PROCESS_REFILL_REQUESTS responsibility
        - Prevents duplicate tasks for the same medication and patient
        
        Returns:
            List containing AddTask effect if task should be created, empty list otherwise.
        """
        log.info(f"Creating refill task for {self.target}, with command {self.context['fields']}")

        # Extract medication name from the refill command
        medication = self.context['fields']['prescribe']['text']
        title = f"Follow up on refill of {medication}"
        patient_id = self.context['patient']['id']

        # Check if a similar task already exists to prevent duplicates
        if Task.objects.filter(title=title, status=TaskStatus.OPEN.value, patient__id=patient_id).exists():
            log.info(f"Refill follow-up task already exists for {medication}, skipping creation")
            return []

        # Find a team with refill processing responsibilities
        team = Team.objects.filter(responsibilities__contains=[TeamResponsibility.PROCESS_REFILL_REQUESTS.value]).values_list('id', flat=True).first()

        log.info(f"Creating refill follow-up task: '{title}' for patient {patient_id}, assigned to team {team}")
        
        return [
            AddTask(
                title=title,
                priority=TaskPriority.URGENT,
                patient_id=patient_id,
                team_id=str(team) if team else None
            ).apply()]

