import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.banner_alert import AddBannerAlert, RemoveBannerAlert
from canvas_sdk.effects.task import TaskPriority
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Task
from logger import log


def json_default_serializer(o):
    """Best-effort serializer for objects that aren't JSON serializable."""
    return str(o)


class UrgentTaskBannerProtocol(BaseProtocol):
    """
    Protocol that manages a patient chart banner based on task urgency.

    - On TASK_CREATED:
        If the task priority is URGENT → add banner.
    - On TASK_PRIORITY_CHANGED:
        If priority changed *to* URGENT → add banner.
        If priority changed *from* URGENT → remove banner.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_PRIORITY_CHANGED),
    ]

    # Constants
    _BANNER_KEY = "task-priority-urgent"
    _BANNER_NARRATIVE = "Patient has urgent task"

    def compute(self) -> list[Effect]:
        task_id = self.event.target.id
        if not task_id:
            log.error("Event target ID is missing; cannot process task.")
            return []

        task = self._get_task(task_id)
        if not task:
            return []

        if self.event.type == EventType.TASK_CREATED:
            return self._handle_created(task)
        elif self.event.type == EventType.TASK_PRIORITY_CHANGED:
            return self._handle_priority_changed(task)

        log.warning(f"Unhandled event type: {self.event.type}")
        return []

    # -------------------------
    # Handlers
    # -------------------------

    def _handle_created(self, task: Task) -> list[Effect]:
        """Handle new task creation: add banner if priority is URGENT."""
        if self._is_priority_urgent(task.priority):
            log.info(f"New task {task.id} is URGENT. Adding banner.")
            return [self._add_banner(task)]
        log.info(f"New task {task.id} is not URGENT. No banner needed.")
        return []

    def _handle_priority_changed(self, task: Task) -> list[Effect]:
        """
        Handle priority change:
        - If changed to URGENT → add banner
        - If changed from URGENT to something else → remove banner
        """
        context = self.event.context or {}
        new_priority = (context.get("new_priority_value") or "").casefold()
        old_priority = (context.get("old_priority_value") or "").casefold()
        urgent_value = TaskPriority.URGENT.value.casefold()

        if new_priority == urgent_value and old_priority != urgent_value:
            log.info(f"Task {task.id} priority changed TO URGENT. Adding banner.")
            return [self._add_banner(task)]

        if old_priority == urgent_value and new_priority != urgent_value:
            log.info(f"Task {task.id} priority changed FROM URGENT. Removing banner.")
            return [self._remove_banner(task)]

        log.info(f"Task {task.id} priority changed, but no banner update required.")
        return []

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _get_task(task_id: str | int) -> Task | None:
        """Fetch a task by ID with error handling."""
        try:
            task = Task.objects.get(id=task_id)
            log.info(
                f"Fetched task: {json.dumps(task, indent=2, default=json_default_serializer)}"
            )
            return task
        except getattr(Task, "DoesNotExist", Exception):
            log.error("Task with id=%s does not exist.", task_id)
        except Exception as e:
            log.exception("Unexpected error fetching task id=%s: %s", task_id, e)
        return None

    @staticmethod
    def _is_priority_urgent(priority_value: str | None) -> bool:
        if not priority_value:
            return False
        return priority_value.casefold() == TaskPriority.URGENT.value.casefold()

    def _add_banner(self, task: Task) -> Effect:
        return AddBannerAlert(
            patient_id=str(task.patient.id),
            key=self._BANNER_KEY,
            narrative=self._BANNER_NARRATIVE,
            placement=[AddBannerAlert.Placement.CHART],
            intent=AddBannerAlert.Intent.INFO,
        ).apply()

    def _remove_banner(self, task: Task) -> Effect:
        return RemoveBannerAlert(
            key=self._BANNER_KEY,
            patient_id=str(task.patient.id),
        ).apply()
