import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.banner_alert import AddBannerAlert, RemoveBannerAlert
from canvas_sdk.effects.task import TaskPriority
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Task
from logger import log


class Protocol(BaseProtocol):
    """
    A protocol that manages banner alerts based on task priority.
    - Adds a banner when a task becomes "Urgent".
    - Removes the banner when a task is no longer "Urgent".
    """

    # This protocol needs to respond to both task creation and updates
    # to correctly track the state of the priority field.
    RESPONDS_TO = EventType.Name(EventType.TASK_CREATED, EventType.TASK_UPDATED)

    def compute(self) -> list[Effect]:
        """Called when a task is created or updated; manages banner alerts accordingly."""
        try:
            task = Task.objects.get(id=self.event.target.id)
        except Task.DoesNotExist:
            log.warning(f"Task with ID {self.event.target.id} not found.")
            return []

        if not task.patient_id:
            log.info(f"Task {task.id} is not associated with a patient; skipping banner logic.")
            return []

        # For created events, there is no "original" context. The `get` default handles this.
        context = self.event.context or {}
        priority_before = context.get("original", {}).get("priority")
        priority_after = task.priority

        effects: list[Effect] = []

        # Condition to ADD the banner: The task is now Urgent, but it wasn't before.
        is_now_urgent = priority_after == TaskPriority.URGENT.value
        was_not_urgent_before = priority_before != TaskPriority.URGENT.value

        if is_now_urgent and was_not_urgent_before:
            log.info(f"Task {task.id} is now Urgent. Adding banner alert for patient {task.patient_id}.")
            effects.append(
                AddBannerAlert(
                    patient_id=str(task.patient_id),
                    key="task-priority-urgent",
                    narrative="Patient has urgent task",
                    placement=[AddBannerAlert.Placement.CHART],
                    intent=AddBannerAlert.Intent.INFO,
                ).apply()
            )

        # Condition to REMOVE the banner: The task was Urgent before, but it isn't now.
        was_urgent_before = priority_before == TaskPriority.URGENT.value
        is_not_urgent_now = priority_after != TaskPriority.URGENT.value

        if was_urgent_before and is_not_urgent_now:
            log.info(f"Task {task.id} is no longer Urgent. Removing banner alert for patient {task.patient_id}.")
            effects.append(
                RemoveBannerAlert(
                    key="task-priority-urgent",
                    patient_id=str(task.patient_id),
                ).apply()
            )

        return effects
