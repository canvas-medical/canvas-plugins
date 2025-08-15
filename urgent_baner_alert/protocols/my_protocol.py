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


class Protocol(BaseProtocol):
    """Protocol that manages an "urgent task" banner on task create/update.

    - On TASK_CREATED or TASK_UPDATED, fetch the Task and inspect its priority.
    - If priority is URGENT → add the banner.
    - If priority is present and not URGENT → remove the banner.
    - If priority is missing/None → do nothing.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_UPDATED),
    ]

    # Banner constants
    _BANNER_KEY = "task-priority-urgent"
    _BANNER_NARRATIVE = "Patient has urgent task"

    def compute(self) -> list[Effect]:
        task_id = self.event.target.id
        if task_id is None:
            log.error("Event target ID is missing; cannot process task.")
            return []

        task = self._get_task(task_id)
        if task is None:
            # Error already logged in _get_task
            return []

        # Normalize priority for case-insensitive comparison
        normalized_priority = (task.priority or "").casefold()
        urgent_value = TaskPriority.URGENT.value.casefold()

        if not normalized_priority:
            # No priority set → no-op
            log.info(
                f"Task {task.id} has no priority set; skipping banner updates."
            )
            return []

        if normalized_priority == urgent_value:
            log.info(
                f"Task {task.id} is URGENT. Ensuring banner '{self._BANNER_KEY}' is present."
            )
            return [self._add_banner(task)]

        log.info(
            f"Task {task.id} priority='{task.priority}' is not URGENT. "
            f"Ensuring banner '{self._BANNER_KEY}' is removed."
        )
        return [self._remove_banner(task)]

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _get_task(task_id: str | int) -> Task | None:
        """Fetch a task by ID with sensible logging and error handling."""
        try:
            task = Task.objects.get(id=task_id)
            # Structured-ish debug payload; falls back to str() on complex fields.
            log.info(
                f"Received event: {json.dumps(task, indent=2, default=json_default_serializer)}"
            )
            return task
        except getattr(Task, "DoesNotExist", Exception):
            log.error("Task with id=%s does not exist.", task_id)
        except Exception as e:  # noqa: BLE001 – we want to log all unexpected errors here
            log.exception("Unexpected error fetching task id=%s: %s", task_id, e)
        return None

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
