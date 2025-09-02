from canvas_sdk.effects import Effect
from canvas_sdk.common.enums import TaskPriority
from canvas_sdk.effects.task import UpdateTask
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Task, Team
from canvas_sdk.v1.data.team import TeamResponsibility
from logger import log


class RefillTaskPriorityProtocol(BaseProtocol):
    """
    A protocol that automatically sets or clears the priority for tasks related to refills.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_UPDATED),
    ]

    def compute(self) -> list[Effect]:
        """
        This method is called when a task is created or updated. It contains the
        core logic to determine if a task's priority needs to be changed.
        """
        task_id = self.event.target.id
        if not task_id:
            log.error("Event target ID is missing; cannot process task.")
            return []

        task = self._get_task(task_id)
        if not task:
            return []

        # Requirement: Only proceed if the task title contains "refill".
        if "refill" not in task.title.casefold():
            log.info(f"Task title '{task.title}' does not contain 'refill'. Skipping.")
            return []

        # Determine what the priority SHOULD be based on the business rules.
        desired_priority = self._get_desired_priority(task)
        current_priority = task.priority

        # Convert the desired priority (an Enum) to its string value for comparison.
        desired_priority_value = desired_priority.value if desired_priority else None

        # To prevent infinite loops, only create an effect if the state needs to change.
        if current_priority == desired_priority_value:
            log.info(f"Task {task.id} priority is already correctly set to '{current_priority}'. No action.")
            return []

        log.info(f"Updating task {task.id} priority from '{current_priority}' to '{desired_priority_value}'.")
        return [UpdateTask(id=str(task.id), priority=desired_priority).apply()]

    def _get_task(self, task_id: str | int) -> Task | None:
        """Fetch a task by ID with error handling."""
        try:
            task = Task.objects.get(id=task_id)
            log.info(f"Task: id={task.id}, title='{task.title}', priority='{task.priority}', team_id={task.team.id}")
            return task
        except Task.DoesNotExist:
            log.error("Task with id=%s does not exist.", task_id)
        except Exception as e:
            log.exception("Unexpected error fetching task id=%s: %s", task_id, e)
        return None

    def _get_desired_priority(self, task: Task) -> TaskPriority | None:
        """
        Determines the correct priority for a task based on its team's responsibilities.
        Returns TaskPriority.URGENT or None.
        """
        if not task.team.id:
            return None

        try:
            team = Team.objects.get(id=task.team.id)
        except Team.DoesNotExist:
            log.warning(f"Team with ID {task.team.id} not found for task {task.id}.")
            return None

        has_responsibility = (
            team.responsibilities and
            TeamResponsibility.PROCESS_REFILL_REQUESTS in team.responsibilities
        )

        if has_responsibility:
            return TaskPriority.URGENT

        return None