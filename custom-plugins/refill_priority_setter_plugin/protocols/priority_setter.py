import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.task import TaskPriority, UpdateTask
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Task
from canvas_sdk.v1.data.team import TeamResponsibility
from logger import log


def json_default_serializer(o):
    """Best-effort serializer for objects that aren't JSON serializable."""
    return str(o)


class RefillTaskPriorityProtocol(BaseProtocol):
    """
    Protocol that sets or clears task priority based on refill task business rules.

    - On TASK_CREATED:
        If task title contains "refill" and the assigned team has the PROCESS_REFILL_REQUESTS
        responsibility, the task is marked as URGENT (unless already urgent).
    - On TASK_UPDATED:
        If the task loses its team assignment, the priority is cleared.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_UPDATED),
    ]

    def compute(self) -> list[Effect]:
        """Main entry point triggered by canvas events."""
        task_id = self.event.target.id
        if not task_id:
            log.error("Event target ID is missing; cannot process task.")
            return []

        task = self._get_task(task_id)
        if not task:
            return []

        if self.event.type == EventType.TASK_CREATED:
            return self._handle_created(task)
        elif self.event.type == EventType.TASK_UPDATED:
            return self._handle_updated(task)

        log.warning(f"Unhandled event type: {self.event.type}")
        return []

    # -------------------------
    # Handlers
    # -------------------------

    def _handle_created(self, task: Task) -> list[Effect]:
        """Assign URGENT priority to new refill request tasks if team supports it."""
        title = getattr(task, "title", "")
        if "refill" not in title.casefold():
            log.info(f"Task title '{title}' does not contain 'refill'. Skipping.")
            return []

        team = getattr(task, "team", None)
        if not team or not getattr(team, "id", None):
            log.info(f"Task {task.id} has no valid team assigned. Skipping.")
            return []

        responsibilities = getattr(team, "responsibilities", [])
        if TeamResponsibility.PROCESS_REFILL_REQUESTS not in responsibilities:
            log.info(f"Team {team.id} is not responsible for processing refills.")
            return []

        if task.priority == TaskPriority.URGENT.value:
            log.info(f"Task {task.id} already has Urgent priority. No update needed.")
            return []

        log.info(f"Task {task.id} qualifies as refill. Setting priority to URGENT.")
        return [self._update_task_priority(task, TaskPriority.URGENT)]

    def _handle_updated(self, task: Task) -> list[Effect]:
        """
        Clear task priority if the task no longer has a team assigned.
        Prevents stale priorities for unassigned tasks.
        """
        team_id = getattr(getattr(task, "team", None), "id", None)
        if team_id is not None:
            log.info(f"Task {task.id} still has team assigned. No action needed.")
            return []

        if task.priority is None:
            log.info(f"Task {task.id} has no team and priority is already cleared.")
            return []

        log.info(f"Task {task.id} lost team assignment. Clearing priority.")
        return [self._update_task_priority(task, None)]

    # -------------------------
    # Helpers
    # -------------------------

    def _get_task(self, task_id: str | int) -> Task | None:
        """Fetch a task by ID with error handling."""
        try:
            task = Task.objects.get(id=task_id)
            log.info(
                f"Fetched task: {json.dumps(task.__dict__, indent=2, default=json_default_serializer)}"
            )
            return task
        except getattr(Task, "DoesNotExist", Exception):
            log.error(f"Task with id={task_id} does not exist.")
        except Exception as e:
            log.exception(f"Unexpected error fetching task id={task_id}: {e}")
        return None

    def _update_task_priority(self, task: Task, priority: str | None) -> Effect:
        """Return an UpdateTask effect to set the new priority."""
        return UpdateTask(id=str(task.id), priority=priority).apply()
