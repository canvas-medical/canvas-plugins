import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.banner_alert import AddBannerAlert, RemoveBannerAlert
from canvas_sdk.effects.patient_metadata import PatientMetadata
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
    Protocol that manages a patient chart banner and metadata based on task urgency.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_PRIORITY_CHANGED),
    ]

    # Constants
    _BANNER_KEY = "task-priority-urgent"
    _BANNER_NARRATIVE = "Patient has urgent task"
    _METADATA_KEY = "Urgent refill"
    _METADATA_VALUE_YES = "Yes"
    _METADATA_VALUE_NO = "No"

    def compute(self) -> list[Effect]:
        """Process the incoming event and determine the necessary effects."""
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
        """Handle new task creation: add banner and metadata if priority is URGENT."""
        if self._is_priority_urgent(task.priority):
            log.info(f"New task {task.id} is URGENT. Adding banner and updating metadata.")
            return self._add_urgent_effects(task)
        log.info(f"New task {task.id} is not URGENT. No action needed.")
        return []

    def _handle_priority_changed(self, task: Task) -> list[Effect]:
        """Handle priority change: add/remove banner and update metadata accordingly."""
        context = self.event.context or {}
        new_priority = (context.get("new_priority_value") or "").casefold()
        old_priority = (context.get("old_priority_value") or "").casefold()
        urgent_value = TaskPriority.URGENT.value.casefold()

        if new_priority == urgent_value and old_priority != urgent_value:
            log.info(f"Task {task.id} priority changed TO URGENT. Adding banner and updating metadata.")
            return self._add_urgent_effects(task)

        if old_priority == urgent_value and new_priority != urgent_value:
            log.info(f"Task {task.id} priority changed FROM URGENT. Removing banner and updating metadata to 'No'.")
            # This line now calls the correctly named helper function.
            return self._remove_urgent_effects(task)

        log.info(f"Task {task.id} priority changed, but no banner/metadata update required.")
        return []

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _get_task(task_id: str | int) -> Task | None:
        """Fetch a task by ID with error handling."""
        try:
            task = Task.objects.get(id=task_id)
            log.info(f"Fetched task: {json.dumps(task, indent=2, default=json_default_serializer)}")
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

    def _add_urgent_effects(self, task: Task) -> list[Effect]:
        """Returns effects to add a banner AND update metadata to 'Yes'."""
        if not task.patient:
            log.warning(f"Task {task.id} is missing a patient. Cannot create effects.")
            return []

        patient_id = str(task.patient.id)

        add_banner_effect = AddBannerAlert(
            patient_id=patient_id,
            key=self._BANNER_KEY,
            narrative=self._BANNER_NARRATIVE,
            placement=[AddBannerAlert.Placement.CHART],
            intent=AddBannerAlert.Intent.INFO,
        ).apply()

        metadata_effect = PatientMetadata(
            patient_id=patient_id, key=self._METADATA_KEY
        ).upsert(value=self._METADATA_VALUE_YES)

        return [add_banner_effect, metadata_effect]

    def _remove_urgent_effects(self, task: Task) -> list[Effect]:
        """Returns effects to remove the banner AND update metadata to 'No'."""
        if not task.patient:
            log.warning(f"Task {task.id} is missing a patient. Cannot create effects.")
            return []

        patient_id = str(task.patient.id)

        remove_banner_effect = RemoveBannerAlert(
            key=self._BANNER_KEY,
            patient_id=patient_id,
        ).apply()

        metadata_effect = PatientMetadata(
            patient_id=patient_id, key=self._METADATA_KEY
        ).upsert(value=self._METADATA_VALUE_NO)

        return [remove_banner_effect, metadata_effect]
